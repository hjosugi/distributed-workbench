package outbox

import (
	"bufio"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sort"
	"sync"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/job"
)

type event struct {
	Kind string    `json:"kind"`
	Job  job.Job   `json:"job,omitempty"`
	ID   string    `json:"id,omitempty"`
	At   time.Time `json:"at"`
}

type Store struct {
	mu      sync.RWMutex
	path    string
	pending map[string]job.Job
	known   map[string]string
}

func Open(path string) (*Store, error) {
	store := &Store{path: path, pending: map[string]job.Job{}, known: map[string]string{}}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return nil, err
	}
	file, err := os.Open(path)
	if errors.Is(err, os.ErrNotExist) {
		return store, nil
	}
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	buffer := make([]byte, 64*1024)
	scanner.Buffer(buffer, 4*1024*1024)
	for scanner.Scan() {
		var item event
		if json.Unmarshal(scanner.Bytes(), &item) != nil {
			continue
		}
		switch item.Kind {
		case "queued":
			store.pending[item.Job.ID] = item.Job
			store.known[item.Job.ID] = "pending"
		case "sent":
			delete(store.pending, item.ID)
			store.known[item.ID] = "sent"
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return store, nil
}

func (s *Store) Queue(value job.Job) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if state, exists := s.known[value.ID]; exists {
		return errors.New("job id already exists with state " + state)
	}
	item := event{Kind: "queued", Job: value, At: time.Now().UTC()}
	if err := s.appendLocked(item); err != nil {
		return err
	}
	s.pending[value.ID] = value
	s.known[value.ID] = "pending"
	return nil
}

func (s *Store) MarkSent(id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.known[id] == "sent" {
		return nil
	}
	if _, exists := s.pending[id]; !exists {
		return errors.New("pending job not found")
	}
	if err := s.appendLocked(event{Kind: "sent", ID: id, At: time.Now().UTC()}); err != nil {
		return err
	}
	delete(s.pending, id)
	s.known[id] = "sent"
	return nil
}

func (s *Store) Pending() []job.Job {
	s.mu.RLock()
	defer s.mu.RUnlock()
	values := make([]job.Job, 0, len(s.pending))
	for _, value := range s.pending {
		values = append(values, value)
	}
	sort.Slice(values, func(i, j int) bool { return values[i].CreatedAt.Before(values[j].CreatedAt) })
	return values
}

func (s *Store) State(id string) (string, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	state, ok := s.known[id]
	return state, ok
}

func (s *Store) appendLocked(item event) error {
	file, err := os.OpenFile(s.path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o600)
	if err != nil {
		return err
	}
	if err := json.NewEncoder(file).Encode(item); err != nil {
		_ = file.Close()
		return err
	}
	if err := file.Sync(); err != nil {
		_ = file.Close()
		return err
	}
	return file.Close()
}
