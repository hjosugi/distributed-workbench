package job

import (
	"bytes"
	"encoding/json"
	"errors"
	"strings"
	"time"
)

type Job struct {
	ID               string          `json:"id"`
	Type             string          `json:"type"`
	Payload          json.RawMessage `json:"payload"`
	CreatedAt        time.Time       `json:"created_at"`
	FailUntilAttempt int             `json:"fail_until_attempt,omitempty"`
	WorkMS           int             `json:"work_ms,omitempty"`
}

func (j *Job) Normalize() {
	j.Type = strings.TrimSpace(j.Type)
	if len(bytes.TrimSpace(j.Payload)) == 0 || bytes.Equal(bytes.TrimSpace(j.Payload), []byte("null")) {
		j.Payload = json.RawMessage(`{}`)
	}
	if j.CreatedAt.IsZero() {
		j.CreatedAt = time.Now().UTC()
	}
}

func (j Job) Validate() error {
	if j.ID == "" {
		return errors.New("job id is required")
	}
	if j.Type == "" || len(j.Type) > 80 {
		return errors.New("type must contain 1 to 80 characters")
	}
	if !json.Valid(j.Payload) {
		return errors.New("payload must be valid JSON")
	}
	if j.FailUntilAttempt < 0 || j.FailUntilAttempt > 1000 {
		return errors.New("fail_until_attempt must be between 0 and 1000")
	}
	if j.WorkMS < 0 || j.WorkMS > 60_000 {
		return errors.New("work_ms must be between 0 and 60000")
	}
	return nil
}
