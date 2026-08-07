package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/job"
	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/metrics"
	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/nsqmini"
	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/processed"
)

type worker struct {
	logger        *slog.Logger
	store         *processed.Store
	counters      *metrics.Counters
	nsqdTCP       string
	nsqdHTTP      string
	topic         string
	channel       string
	dlqTopic      string
	maxAttempts   int
	baseRequeue   time.Duration
	publishClient *http.Client
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	store, err := processed.Open(env("PROCESSED_FILE", "./data/processed.jsonl"))
	if err != nil {
		logger.Error("failed to open processed store", "error", err)
		os.Exit(1)
	}
	maxAttempts, err := strconv.Atoi(env("MAX_ATTEMPTS", "5"))
	if err != nil || maxAttempts < 1 {
		logger.Error("invalid MAX_ATTEMPTS")
		os.Exit(1)
	}
	baseRequeue, err := time.ParseDuration(env("BASE_REQUEUE_DELAY", "2s"))
	if err != nil || baseRequeue < 0 {
		logger.Error("invalid BASE_REQUEUE_DELAY")
		os.Exit(1)
	}
	w := &worker{
		logger: logger, store: store, counters: &metrics.Counters{},
		nsqdTCP:  env("NSQD_TCP_ADDRESS", "localhost:4150"),
		nsqdHTTP: env("NSQD_HTTP_URL", "http://localhost:4151"),
		topic:    env("NSQ_TOPIC", "jobs"), channel: env("NSQ_CHANNEL", "processor"),
		dlqTopic: env("NSQ_DLQ_TOPIC", "jobs_dlq"), maxAttempts: maxAttempts,
		baseRequeue: baseRequeue, publishClient: &http.Client{Timeout: 5 * time.Second},
	}
	for _, value := range []string{w.topic, w.channel, w.dlqTopic} {
		if err := nsqmini.ValidateName(value); err != nil {
			logger.Error("invalid NSQ name", "value", value, "error", err)
			os.Exit(1)
		}
	}

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	go w.serveMetrics(ctx, env("METRICS_ADDR", ":8083"))

	for ctx.Err() == nil {
		if err := w.consume(ctx); err != nil && ctx.Err() == nil {
			w.counters.Errors.Add(1)
			logger.Warn("consumer disconnected; retrying", "error", err)
			select {
			case <-ctx.Done():
			case <-time.After(2 * time.Second):
			}
		}
	}
}

func (w *worker) consume(ctx context.Context) error {
	consumer, err := nsqmini.Dial(ctx, w.nsqdTCP, 5*time.Second)
	if err != nil {
		return err
	}
	defer consumer.Close()
	consumerDone := make(chan struct{})
	defer close(consumerDone)
	go func() {
		select {
		case <-ctx.Done():
			_ = consumer.Close()
		case <-consumerDone:
		}
	}()
	if err := consumer.Identify(nsqmini.IdentifyOptions{FeatureNegotiation: true}); err != nil {
		return err
	}
	if err := consumer.Subscribe(w.topic, w.channel); err != nil {
		return err
	}
	if err := consumer.Ready(1); err != nil {
		return err
	}
	w.logger.Info("consumer connected", "nsqd", w.nsqdTCP, "topic", w.topic, "channel", w.channel)

	for ctx.Err() == nil {
		message, err := consumer.Next()
		if err != nil {
			return err
		}
		w.counters.Received.Add(1)
		if err := w.handle(ctx, consumer, message); err != nil {
			w.counters.Errors.Add(1)
			return err
		}
		if err := consumer.Ready(1); err != nil {
			return err
		}
	}
	return ctx.Err()
}

func (w *worker) handle(ctx context.Context, consumer *nsqmini.Consumer, message nsqmini.Message) error {
	var value job.Job
	if err := json.Unmarshal(message.Body, &value); err != nil {
		return w.fail(ctx, consumer, message, nil, "invalid job JSON: "+err.Error())
	}
	value.Normalize()
	if err := value.Validate(); err != nil {
		return w.fail(ctx, consumer, message, &value, "invalid job: "+err.Error())
	}
	if w.store.Has(value.ID) {
		w.counters.Duplicates.Add(1)
		w.logger.Info("duplicate skipped", "job_id", value.ID, "message_id", message.ID)
		return consumer.Finish(message.ID)
	}
	if int(message.Attempts) <= value.FailUntilAttempt {
		return w.fail(ctx, consumer, message, &value, "intentional demo failure")
	}
	if value.WorkMS > 0 {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(time.Duration(value.WorkMS) * time.Millisecond):
		}
	}
	inserted, err := w.store.Mark(processed.Record{Job: value, MessageID: message.ID, Attempts: message.Attempts})
	if err != nil {
		return err
	}
	if !inserted {
		w.counters.Duplicates.Add(1)
	} else {
		w.counters.Processed.Add(1)
	}
	w.logger.Info("job processed", "job_id", value.ID, "attempts", message.Attempts)
	return consumer.Finish(message.ID)
}

func (w *worker) fail(ctx context.Context, consumer *nsqmini.Consumer, message nsqmini.Message, value *job.Job, reason string) error {
	if int(message.Attempts) >= w.maxAttempts {
		envelope := map[string]any{
			"reason": reason, "attempts": message.Attempts, "message_id": message.ID,
			"failed_at": time.Now().UTC(), "raw_body_base64": base64.StdEncoding.EncodeToString(message.Body),
		}
		if value != nil {
			envelope["job"] = value
		}
		body, _ := json.Marshal(envelope)
		publishCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
		err := nsqmini.PublishHTTP(publishCtx, w.publishClient, w.nsqdHTTP, w.dlqTopic, body)
		cancel()
		if err != nil {
			return fmt.Errorf("DLQ publish failed: %w", err)
		}
		w.counters.DLQ.Add(1)
		w.logger.Warn("job sent to DLQ", "message_id", message.ID, "attempts", message.Attempts, "reason", reason)
		return consumer.Finish(message.ID)
	}
	delay := retryDelay(w.baseRequeue, message.Attempts)
	w.counters.Retries.Add(1)
	w.logger.Warn("job requeued", "message_id", message.ID, "attempts", message.Attempts, "delay", delay, "reason", reason)
	return consumer.Requeue(message.ID, delay)
}

func retryDelay(base time.Duration, attempts uint16) time.Duration {
	exponent := int(attempts) - 1
	if exponent < 0 {
		exponent = 0
	}
	// The one-minute cap means larger exponents provide no useful precision.
	if exponent > 10 {
		exponent = 10
	}
	delay := base * time.Duration(1<<exponent)
	if delay < 0 || delay > time.Minute {
		return time.Minute
	}
	return delay
}

func (w *worker) serveMetrics(ctx context.Context, address string) {
	mux := http.NewServeMux()
	mux.Handle("GET /metrics", w.counters.Handler(w.store.Count))
	mux.HandleFunc("GET /healthz", func(response http.ResponseWriter, _ *http.Request) {
		response.Header().Set("Content-Type", "application/json")
		_, _ = response.Write([]byte(`{"status":"ok"}`))
	})
	server := &http.Server{Addr: address, Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	go func() {
		<-ctx.Done()
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(shutdownCtx)
	}()
	w.logger.Info("metrics server started", "address", address)
	if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		w.logger.Error("metrics server failed", "error", err)
	}
}

func env(name, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(name)); value != "" {
		return value
	}
	return fallback
}
