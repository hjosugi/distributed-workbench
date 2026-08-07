package processed

import (
	"encoding/json"
	"path/filepath"
	"testing"

	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/job"
)

func TestMarkIsIdempotent(t *testing.T) {
	t.Parallel()
	store, err := Open(filepath.Join(t.TempDir(), "processed.jsonl"))
	if err != nil {
		t.Fatal(err)
	}
	record := Record{Job: job.Job{ID: "same", Type: "test", Payload: json.RawMessage(`{}`)}, MessageID: "message-1", Attempts: 1}
	inserted, err := store.Mark(record)
	if err != nil || !inserted {
		t.Fatalf("first mark failed: inserted=%v err=%v", inserted, err)
	}
	inserted, err = store.Mark(record)
	if err != nil || inserted {
		t.Fatalf("second mark should be duplicate: inserted=%v err=%v", inserted, err)
	}
}
