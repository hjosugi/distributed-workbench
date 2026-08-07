package history

import (
	"path/filepath"
	"testing"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/harbor-observer/internal/probe"
)

func TestStorePersistsAndReloads(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "history.jsonl")
	store, err := Open(path, 10)
	if err != nil {
		t.Fatal(err)
	}
	run := probe.Run{ID: "one", Path: "/status", StartedAt: time.Now(), FinishedAt: time.Now()}
	if err := store.Append(run); err != nil {
		t.Fatal(err)
	}
	reloaded, err := Open(path, 10)
	if err != nil {
		t.Fatal(err)
	}
	runs := reloaded.Recent(10)
	if len(runs) != 1 || runs[0].ID != "one" {
		t.Fatalf("unexpected runs: %+v", runs)
	}
}
