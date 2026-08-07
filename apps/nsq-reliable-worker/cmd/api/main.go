package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"regexp"
	"strings"
	"syscall"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/job"
	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/nsqmini"
	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/outbox"
)

var idempotencyPattern = regexp.MustCompile(`^[A-Za-z0-9._:-]{1,128}$`)

type app struct {
	logger     *slog.Logger
	store      *outbox.Store
	nsqURL     string
	topic      string
	httpClient *http.Client
	notify     chan struct{}
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	store, err := outbox.Open(env("OUTBOX_FILE", "./data/outbox.jsonl"))
	if err != nil {
		logger.Error("failed to open outbox", "error", err)
		os.Exit(1)
	}
	application := &app{
		logger:     logger,
		store:      store,
		nsqURL:     env("NSQD_HTTP_URL", "http://localhost:4151"),
		topic:      env("NSQ_TOPIC", "jobs"),
		httpClient: &http.Client{Timeout: 5 * time.Second},
		notify:     make(chan struct{}, 1),
	}
	if err := nsqmini.ValidateName(application.topic); err != nil {
		logger.Error("invalid NSQ_TOPIC", "error", err)
		os.Exit(1)
	}

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	go application.dispatchLoop(ctx)

	mux := http.NewServeMux()
	mux.HandleFunc("GET /", application.home)
	mux.HandleFunc("GET /healthz", application.health)
	mux.HandleFunc("GET /jobs/pending", application.pending)
	mux.HandleFunc("POST /jobs", application.createJob)
	mux.HandleFunc("POST /dispatch", application.forceDispatch)

	server := &http.Server{
		Addr:              env("LISTEN_ADDR", ":8082"),
		Handler:           securityHeaders(mux),
		ReadHeaderTimeout: 5 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	go func() {
		logger.Info("NSQ job API started", "address", server.Addr, "topic", application.topic)
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logger.Error("server failed", "error", err)
			os.Exit(1)
		}
	}()
	<-ctx.Done()
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = server.Shutdown(shutdownCtx)
}

func (a *app) createJob(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var request struct {
		Type             string          `json:"type"`
		Payload          json.RawMessage `json:"payload"`
		FailUntilAttempt int             `json:"fail_until_attempt"`
		WorkMS           int             `json:"work_ms"`
	}
	decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&request); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "invalid JSON: " + err.Error()})
		return
	}
	id := strings.TrimSpace(r.Header.Get("Idempotency-Key"))
	if id == "" {
		id = newID()
	} else if !idempotencyPattern.MatchString(id) {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "Idempotency-Key contains unsupported characters"})
		return
	}
	value := job.Job{
		ID: id, Type: request.Type, Payload: request.Payload, CreatedAt: time.Now().UTC(),
		FailUntilAttempt: request.FailUntilAttempt, WorkMS: request.WorkMS,
	}
	value.Normalize()
	if err := value.Validate(); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": err.Error()})
		return
	}
	if err := a.store.Queue(value); err != nil {
		writeJSON(w, http.StatusConflict, map[string]any{"error": err.Error(), "id": id})
		return
	}
	a.wakeDispatcher()
	writeJSON(w, http.StatusAccepted, map[string]any{"job": value, "state": "pending"})
}

func (a *app) pending(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{"jobs": a.store.Pending()})
}

func (a *app) forceDispatch(w http.ResponseWriter, _ *http.Request) {
	a.wakeDispatcher()
	writeJSON(w, http.StatusAccepted, map[string]any{"status": "scheduled"})
}

func (a *app) health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{"status": "ok", "pending": len(a.store.Pending())})
}

func (a *app) dispatchLoop(ctx context.Context) {
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			a.dispatch(ctx)
		case <-a.notify:
			a.dispatch(ctx)
		}
	}
}

func (a *app) dispatch(ctx context.Context) {
	for _, value := range a.store.Pending() {
		body, err := json.Marshal(value)
		if err != nil {
			a.logger.Error("failed to encode job", "job_id", value.ID, "error", err)
			continue
		}
		publishCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
		err = nsqmini.PublishHTTP(publishCtx, a.httpClient, a.nsqURL, a.topic, body)
		cancel()
		if err != nil {
			a.logger.Warn("publish failed; job remains in outbox", "job_id", value.ID, "error", err)
			return
		}
		if err := a.store.MarkSent(value.ID); err != nil {
			a.logger.Error("published but failed to mark sent; duplicate publish is possible", "job_id", value.ID, "error", err)
			return
		}
		a.logger.Info("job published", "job_id", value.ID, "topic", a.topic)
	}
}

func (a *app) wakeDispatcher() {
	select {
	case a.notify <- struct{}{}:
	default:
	}
}

func (a *app) home(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_, _ = fmt.Fprint(w, `<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>NSQ Reliable Worker</title><style>body{font-family:system-ui;max-width:760px;margin:48px auto;padding:0 20px;color:#172033}form{display:grid;gap:12px;padding:20px;border:1px solid #ddd;border-radius:14px}input,textarea,button{font:inherit;padding:10px}textarea{min-height:100px}button{background:#2767f6;color:white;border:0;border-radius:8px;font-weight:700}pre{background:#101827;color:#dbe7ff;padding:16px;border-radius:12px;overflow:auto}</style><h1>NSQ Reliable Worker</h1><p>Jobはdurable outboxに保存され、NSQへpublishされます。</p><form id="form"><input name="type" value="send-email"><input name="key" value="demo-001" placeholder="Idempotency-Key"><textarea name="payload">{"to":"demo@example.com"}</textarea><label>fail until attempt <input name="fail" type="number" value="2"></label><button>Submit job</button></form><pre id="result">Ready.</pre><p><a href="/jobs/pending">Pending jobs</a></p><script>document.querySelector('#form').addEventListener('submit',async(e)=>{e.preventDefault();const f=new FormData(e.target);let payload;try{payload=JSON.parse(f.get('payload'))}catch(err){alert(err);return}const r=await fetch('/jobs',{method:'POST',headers:{'content-type':'application/json','Idempotency-Key':f.get('key')},body:JSON.stringify({type:f.get('type'),payload,fail_until_attempt:Number(f.get('fail'))})});document.querySelector('#result').textContent=JSON.stringify(await r.json(),null,2)});</script></html>`)
}

func newID() string {
	var value [16]byte
	if _, err := rand.Read(value[:]); err != nil {
		return fmt.Sprintf("job-%d", time.Now().UnixNano())
	}
	return hex.EncodeToString(value[:])
}

func env(name, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(name)); value != "" {
		return value
	}
	return fallback
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}

func securityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Referrer-Policy", "no-referrer")
		w.Header().Set("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'")
		next.ServeHTTP(w, r)
	})
}
