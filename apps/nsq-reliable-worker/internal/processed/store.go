package processed

import (
	"bufio"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/hjosugi/distributed-workbench/apps/nsq-reliable-worker/internal/job"
)

type Record struct {
	Job       job.Job   `json:"job"`
	MessageID string    `json:"message_id"`
	Attempts  uint16    `json:"attempts"`
	At        time.Time `json:"processed_at"`
}

type Store struct {
	mu      sync.RWMutex
	path    string
	records map[string]Record
}

func Open(path string) (*Store, error) {
	store := &Store{path: path, records: map[string]Record{}}
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
		var record Record
		if json.Unmarshal(scanner.Bytes(), &record) == nil && record.Job.ID != "" {
			store.records[record.Job.ID] = record
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return store, nil
}

func (s *Store) Has(jobID string) bool {
	s.mu.RLock()
	defer s.mu.RUnlock()
	_, exists := s.records[jobID]
	return exists
}

// Mark is the durable demo business effect. It is written before FIN so a
// redelivery after a crash can be acknowledged without applying the effect twice.
func (s *Store) Mark(record Record) (bool, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, exists := s.records[record.Job.ID]; exists {
		return false, nil
	}
	if record.At.IsZero() {
		record.At = time.Now().UTC()
	}
	file, err := os.OpenFile(s.path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o600)
	if err != nil {
		return false, err
	}
	if err := json.NewEncoder(file).Encode(record); err != nil {
		_ = file.Close()
		return false, err
	}
	if err := file.Sync(); err != nil {
		_ = file.Close()
		return false, err
	}
	if err := file.Close(); err != nil {
		return false, err
	}
	s.records[record.Job.ID] = record
	return true, nil
}

func (s *Store) Count() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.records)
}
