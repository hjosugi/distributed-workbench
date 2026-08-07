package probe

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestValidatePath(t *testing.T) {
	t.Parallel()
	valid := []string{"/status", "/blob/abc", "/path?q=1"}
	for _, value := range valid {
		if err := ValidatePath(value); err != nil {
			t.Fatalf("expected %q to be valid: %v", value, err)
		}
	}
	invalid := []string{"", "status", "https://example.com/status", "//example.com/status"}
	for _, value := range invalid {
		if err := ValidatePath(value); err == nil {
			t.Fatalf("expected %q to be invalid", value)
		}
	}
}

func TestRunDetectsDivergence(t *testing.T) {
	t.Parallel()
	serverA := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte("same"))
	}))
	defer serverA.Close()
	serverB := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte("different"))
	}))
	defer serverB.Close()

	p := New(&http.Client{Timeout: time.Second}, 1024)
	run, err := p.Run(context.Background(), "test", "/status", []Server{
		{Name: "a", BaseURL: serverA.URL},
		{Name: "b", BaseURL: serverB.URL},
	})
	if err != nil {
		t.Fatal(err)
	}
	if run.Summary.State != "divergent" {
		t.Fatalf("expected divergent, got %+v", run.Summary)
	}
	if run.Summary.VariantCount != 2 {
		t.Fatalf("expected 2 variants, got %d", run.Summary.VariantCount)
	}
}

func TestRunHealthy(t *testing.T) {
	t.Parallel()
	newServer := func() *httptest.Server {
		return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
			w.Header().Set("Content-Type", "text/plain")
			_, _ = w.Write([]byte("OK."))
		}))
	}
	serverA := newServer()
	defer serverA.Close()
	serverB := newServer()
	defer serverB.Close()

	p := New(&http.Client{Timeout: time.Second}, 1024)
	run, err := p.Run(context.Background(), "test", "/status", []Server{
		{Name: "a", BaseURL: serverA.URL},
		{Name: "b", BaseURL: serverB.URL},
	})
	if err != nil {
		t.Fatal(err)
	}
	if run.Summary.State != "healthy" || !run.Summary.Consistent {
		t.Fatalf("expected healthy, got %+v", run.Summary)
	}
}
