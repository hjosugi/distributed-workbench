package web

import (
	"context"
	"crypto/rand"
	"embed"
	"encoding/hex"
	"encoding/json"
	"io/fs"
	"log/slog"
	"net/http"
	"strconv"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/harbor-observer/internal/history"
	"github.com/hjosugi/distributed-workbench/apps/harbor-observer/internal/probe"
)

//go:embed assets/*
var assets embed.FS

type Server struct {
	logger  *slog.Logger
	servers []probe.Server
	prober  *probe.Prober
	history *history.Store
}

func NewHandler(logger *slog.Logger, servers []probe.Server, prober *probe.Prober, store *history.Store) http.Handler {
	server := &Server{logger: logger, servers: servers, prober: prober, history: store}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", server.health)
	mux.HandleFunc("GET /api/config", server.config)
	mux.HandleFunc("GET /api/probes", server.listProbes)
	mux.HandleFunc("POST /api/probes", server.createProbe)

	sub, err := fs.Sub(assets, "assets")
	if err != nil {
		panic(err)
	}
	mux.Handle("/", http.FileServer(http.FS(sub)))
	return securityHeaders(mux)
}

func (s *Server) health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{"status": "ok"})
}

func (s *Server) config(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{"servers": s.servers})
}

func (s *Server) listProbes(w http.ResponseWriter, r *http.Request) {
	limit := 20
	if raw := r.URL.Query().Get("limit"); raw != "" {
		if parsed, err := strconv.Atoi(raw); err == nil && parsed > 0 && parsed <= 200 {
			limit = parsed
		}
	}
	writeJSON(w, http.StatusOK, map[string]any{"runs": s.history.Recent(limit)})
}

func (s *Server) createProbe(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var request struct {
		Path string `json:"path"`
	}
	decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, 32*1024))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&request); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "invalid JSON: " + err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 30*time.Second)
	defer cancel()
	run, err := s.prober.Run(ctx, newID(), request.Path, s.servers)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": err.Error()})
		return
	}
	if err := s.history.Append(run); err != nil {
		s.logger.Error("failed to persist probe", "error", err)
		writeJSON(w, http.StatusInternalServerError, map[string]any{"error": "probe completed but history could not be saved"})
		return
	}
	writeJSON(w, http.StatusOK, run)
}

func newID() string {
	var value [8]byte
	if _, err := rand.Read(value[:]); err != nil {
		return strconv.FormatInt(time.Now().UnixNano(), 36)
	}
	return hex.EncodeToString(value[:])
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
		w.Header().Set("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:")
		next.ServeHTTP(w, r)
	})
}
