package metrics

import (
	"fmt"
	"net/http"
	"sync/atomic"
)

type Counters struct {
	Received   atomic.Uint64
	Processed  atomic.Uint64
	Duplicates atomic.Uint64
	Retries    atomic.Uint64
	DLQ        atomic.Uint64
	Errors     atomic.Uint64
}

func (c *Counters) Handler(processedCount func() int) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
		_, _ = fmt.Fprintf(w, "nsq_worker_received_total %d\n", c.Received.Load())
		_, _ = fmt.Fprintf(w, "nsq_worker_processed_total %d\n", c.Processed.Load())
		_, _ = fmt.Fprintf(w, "nsq_worker_duplicates_total %d\n", c.Duplicates.Load())
		_, _ = fmt.Fprintf(w, "nsq_worker_retries_total %d\n", c.Retries.Load())
		_, _ = fmt.Fprintf(w, "nsq_worker_dlq_total %d\n", c.DLQ.Load())
		_, _ = fmt.Fprintf(w, "nsq_worker_errors_total %d\n", c.Errors.Load())
		_, _ = fmt.Fprintf(w, "nsq_worker_processed_store_records %d\n", processedCount())
	})
}
