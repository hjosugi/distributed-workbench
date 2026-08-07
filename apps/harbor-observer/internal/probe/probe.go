package probe

import (
	"context"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"sort"
	"strings"
	"sync"
	"time"
	"unicode"
	"unicode/utf8"
)

const defaultMaxBodyBytes int64 = 8 << 20

type Server struct {
	Name    string `json:"name"`
	BaseURL string `json:"base_url"`
}

type Result struct {
	Server      string `json:"server"`
	BaseURL     string `json:"base_url"`
	URL         string `json:"url"`
	Reachable   bool   `json:"reachable"`
	Status      int    `json:"status,omitempty"`
	LatencyMS   int64  `json:"latency_ms"`
	Bytes       int    `json:"bytes"`
	SHA256      string `json:"sha256,omitempty"`
	ContentType string `json:"content_type,omitempty"`
	Preview     string `json:"preview,omitempty"`
	Truncated   bool   `json:"truncated"`
	Error       string `json:"error,omitempty"`
}

type Summary struct {
	Total        int     `json:"total"`
	Reachable    int     `json:"reachable"`
	Coverage     float64 `json:"coverage"`
	VariantCount int     `json:"variant_count"`
	Consistent   bool    `json:"consistent"`
	State        string  `json:"state"`
}

type Run struct {
	ID         string    `json:"id"`
	Path       string    `json:"path"`
	StartedAt  time.Time `json:"started_at"`
	FinishedAt time.Time `json:"finished_at"`
	Results    []Result  `json:"results"`
	Summary    Summary   `json:"summary"`
}

type Prober struct {
	Client       *http.Client
	MaxBodyBytes int64
}

func New(client *http.Client, maxBodyBytes int64) *Prober {
	if client == nil {
		client = &http.Client{Timeout: 5 * time.Second}
	}
	if maxBodyBytes <= 0 {
		maxBodyBytes = defaultMaxBodyBytes
	}
	return &Prober{Client: client, MaxBodyBytes: maxBodyBytes}
}

func ValidatePath(raw string) error {
	if raw == "" || !strings.HasPrefix(raw, "/") {
		return errors.New("path must start with /")
	}
	u, err := url.Parse(raw)
	if err != nil {
		return fmt.Errorf("invalid path: %w", err)
	}
	if u.IsAbs() || u.Host != "" || u.Scheme != "" {
		return errors.New("absolute URLs are not allowed")
	}
	if strings.HasPrefix(raw, "//") {
		return errors.New("network-path references are not allowed")
	}
	return nil
}

func (p *Prober) Run(ctx context.Context, id, path string, servers []Server) (Run, error) {
	if err := ValidatePath(path); err != nil {
		return Run{}, err
	}
	started := time.Now().UTC()
	results := make([]Result, len(servers))

	var wg sync.WaitGroup
	for i, server := range servers {
		i, server := i, server
		wg.Add(1)
		go func() {
			defer wg.Done()
			results[i] = p.probeOne(ctx, path, server)
		}()
	}
	wg.Wait()

	sort.Slice(results, func(i, j int) bool { return results[i].Server < results[j].Server })
	return Run{
		ID:         id,
		Path:       path,
		StartedAt:  started,
		FinishedAt: time.Now().UTC(),
		Results:    results,
		Summary:    Summarize(results),
	}, nil
}

func (p *Prober) probeOne(ctx context.Context, path string, server Server) Result {
	base := strings.TrimRight(server.BaseURL, "/")
	target := base + path
	result := Result{Server: server.Name, BaseURL: server.BaseURL, URL: target}

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, target, nil)
	if err != nil {
		result.Error = err.Error()
		return result
	}
	req.Header.Set("Accept", "*/*")
	req.Header.Set("User-Agent", "distributed-workbench-harbor-observer/0.1")

	started := time.Now()
	resp, err := p.Client.Do(req)
	result.LatencyMS = time.Since(started).Milliseconds()
	if err != nil {
		result.Error = err.Error()
		return result
	}
	defer resp.Body.Close()

	data, readErr := io.ReadAll(io.LimitReader(resp.Body, p.MaxBodyBytes+1))
	if readErr != nil {
		result.Error = readErr.Error()
		return result
	}
	if int64(len(data)) > p.MaxBodyBytes {
		result.Truncated = true
		data = data[:p.MaxBodyBytes]
	}

	digest := sha256.Sum256(data)
	result.Reachable = true
	result.Status = resp.StatusCode
	result.Bytes = len(data)
	result.SHA256 = hex.EncodeToString(digest[:])
	result.ContentType = resp.Header.Get("Content-Type")
	result.Preview = makePreview(data)
	return result
}

func Summarize(results []Result) Summary {
	summary := Summary{Total: len(results)}
	variants := map[string]struct{}{}
	for _, result := range results {
		if !result.Reachable {
			continue
		}
		summary.Reachable++
		variants[fmt.Sprintf("%d:%s:%t", result.Status, result.SHA256, result.Truncated)] = struct{}{}
	}
	if summary.Total > 0 {
		summary.Coverage = float64(summary.Reachable) / float64(summary.Total)
	}
	summary.VariantCount = len(variants)
	summary.Consistent = summary.Reachable > 0 && summary.VariantCount == 1

	switch {
	case summary.Reachable == 0:
		summary.State = "unavailable"
	case summary.VariantCount > 1:
		summary.State = "divergent"
	case summary.Reachable == 1:
		summary.State = "single-copy-risk"
	default:
		summary.State = "healthy"
	}
	return summary
}

func makePreview(data []byte) string {
	const maxText = 240
	if len(data) == 0 {
		return ""
	}
	if utf8.Valid(data) && mostlyPrintable(string(data)) {
		runes := []rune(strings.ToValidUTF8(string(data), "�"))
		if len(runes) > maxText {
			runes = runes[:maxText]
		}
		return string(runes)
	}
	limit := len(data)
	if limit > 120 {
		limit = 120
	}
	return "base64:" + base64.StdEncoding.EncodeToString(data[:limit])
}

func mostlyPrintable(value string) bool {
	if value == "" {
		return true
	}
	printable := 0
	total := 0
	for _, r := range value {
		total++
		if unicode.IsPrint(r) || r == '\n' || r == '\r' || r == '\t' {
			printable++
		}
	}
	return total == 0 || float64(printable)/float64(total) >= 0.9
}
