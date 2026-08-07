package main

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/harbor-observer/internal/history"
	"github.com/hjosugi/distributed-workbench/apps/harbor-observer/internal/probe"
	webapp "github.com/hjosugi/distributed-workbench/apps/harbor-observer/internal/web"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	servers, err := parseServers(env("HARBOR_SERVERS", "local=http://localhost:3000"))
	if err != nil {
		logger.Error("invalid HARBOR_SERVERS", "error", err)
		os.Exit(1)
	}
	timeout, err := time.ParseDuration(env("PROBE_TIMEOUT", "5s"))
	if err != nil {
		logger.Error("invalid PROBE_TIMEOUT", "error", err)
		os.Exit(1)
	}
	maxBody, err := strconv.ParseInt(env("MAX_BODY_BYTES", "8388608"), 10, 64)
	if err != nil || maxBody <= 0 {
		logger.Error("invalid MAX_BODY_BYTES")
		os.Exit(1)
	}
	store, err := history.Open(env("HISTORY_FILE", "./data/probes.jsonl"), 200)
	if err != nil {
		logger.Error("failed to open history", "error", err)
		os.Exit(1)
	}

	client := &http.Client{Timeout: timeout}
	handler := webapp.NewHandler(logger, servers, probe.New(client, maxBody), store)
	server := &http.Server{
		Addr:              env("LISTEN_ADDR", ":8081"),
		Handler:           handler,
		ReadHeaderTimeout: 5 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	go func() {
		logger.Info("harbor observer started", "address", server.Addr, "servers", len(servers))
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logger.Error("server stopped", "error", err)
			os.Exit(1)
		}
	}()

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	<-ctx.Done()
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := server.Shutdown(shutdownCtx); err != nil {
		logger.Error("shutdown failed", "error", err)
	}
}

func env(name, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(name)); value != "" {
		return value
	}
	return fallback
}

func parseServers(raw string) ([]probe.Server, error) {
	parts := strings.Split(raw, ",")
	servers := make([]probe.Server, 0, len(parts))
	seen := map[string]struct{}{}
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}
		name, baseURL, ok := strings.Cut(part, "=")
		if !ok || strings.TrimSpace(name) == "" || strings.TrimSpace(baseURL) == "" {
			return nil, errors.New("expected comma-separated name=https://server entries")
		}
		name = strings.TrimSpace(name)
		baseURL = strings.TrimRight(strings.TrimSpace(baseURL), "/")
		parsed, err := url.Parse(baseURL)
		if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.Host == "" {
			return nil, errors.New("server URL must be absolute http or https")
		}
		if _, exists := seen[name]; exists {
			return nil, errors.New("server names must be unique")
		}
		seen[name] = struct{}{}
		servers = append(servers, probe.Server{Name: name, BaseURL: baseURL})
	}
	if len(servers) == 0 {
		return nil, errors.New("at least one server is required")
	}
	return servers, nil
}
