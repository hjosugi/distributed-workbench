package history

import (
	"bufio"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sync"

	"github.com/hjosugi/distributed-workbench/apps/harbor-observer/internal/probe"
)

type Store struct {
	mu   sync.RWMutex
	path string
	max  int
	runs []probe.Run
}

func Open(path string, max int) (*Store, error) {
	if max <= 0 {
		max = 200
	}
	store := &Store{path: path, max: max}
	if path == "" {
		return store, nil
	}
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
		var run probe.Run
		if json.Unmarshal(scanner.Bytes(), &run) == nil {
			store.runs = append(store.runs, run)
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	store.trimLocked()
	return store, nil
}

func (s *Store) Append(run probe.Run) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.path != "" {
		file, err := os.OpenFile(s.path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644)
		if err != nil {
			return err
		}
		encoder := json.NewEncoder(file)
		if err := encoder.Encode(run); err != nil {
			_ = file.Close()
			return err
		}
		if err := file.Sync(); err != nil {
			_ = file.Close()
			return err
		}
		if err := file.Close(); err != nil {
			return err
		}
	}

	s.runs = append(s.runs, run)
	s.trimLocked()
	return nil
}

func (s *Store) Recent(limit int) []probe.Run {
	s.mu.RLock()
	defer s.mu.RUnlock()
	if limit <= 0 || limit > len(s.runs) {
		limit = len(s.runs)
	}
	result := make([]probe.Run, 0, limit)
	for i := len(s.runs) - 1; i >= 0 && len(result) < limit; i-- {
		result = append(result, s.runs[i])
	}
	return result
}

func (s *Store) trimLocked() {
	if len(s.runs) <= s.max {
		return
	}
	start := len(s.runs) - s.max
	trimmed := make([]probe.Run, s.max)
	copy(trimmed, s.runs[start:])
	s.runs = trimmed
}
