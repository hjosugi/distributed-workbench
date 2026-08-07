package outbox

import (
	"encoding/json"
	"path/filepath"
	"testing"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/job"
)

func TestStoreRecoversPendingJobs(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "outbox.jsonl")
	store, err := Open(path)
	if err != nil {
		t.Fatal(err)
	}
	value := job.Job{ID: "job-1", Type: "test", Payload: json.RawMessage(`{"ok":true}`), CreatedAt: time.Now()}
	if err := store.Queue(value); err != nil {
		t.Fatal(err)
	}
	reloaded, err := Open(path)
	if err != nil {
		t.Fatal(err)
	}
	if len(reloaded.Pending()) != 1 {
		t.Fatalf("expected one pending job, got %d", len(reloaded.Pending()))
	}
	if err := reloaded.MarkSent("job-1"); err != nil {
		t.Fatal(err)
	}
	again, err := Open(path)
	if err != nil {
		t.Fatal(err)
	}
	if len(again.Pending()) != 0 {
		t.Fatalf("expected no pending jobs, got %d", len(again.Pending()))
	}
	if state, ok := again.State("job-1"); !ok || state != "sent" {
		t.Fatalf("unexpected state: %q, %v", state, ok)
	}
}
