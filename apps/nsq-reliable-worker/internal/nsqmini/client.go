package nsqmini

import (
	"bufio"
	"bytes"
	"context"
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"sync"
	"time"
)

const (
	FrameResponse int32 = 0
	FrameError    int32 = 1
	FrameMessage  int32 = 2
	maxFrameSize        = 100 << 20
)

var namePattern = regexp.MustCompile(`^[A-Za-z0-9._-]+(?:#ephemeral)?$`)

type Frame struct {
	Type int32
	Data []byte
}

type Message struct {
	Timestamp int64
	Attempts  uint16
	ID        string
	Body      []byte
}

type IdentifyOptions struct {
	ClientID           string `json:"client_id"`
	Hostname           string `json:"hostname"`
	FeatureNegotiation bool   `json:"feature_negotiation"`
	HeartbeatInterval  int    `json:"heartbeat_interval"`
	OutputBufferTime   int    `json:"output_buffer_timeout"`
}

type Consumer struct {
	conn   net.Conn
	reader *bufio.Reader
	writer *bufio.Writer
	mu     sync.Mutex
}

func ValidateName(value string) error {
	if len(value) < 1 || len(value) > 64 || !namePattern.MatchString(value) {
		return errors.New("NSQ topic/channel must be 1-64 characters using A-Z, a-z, 0-9, ., _, - and optional #ephemeral")
	}
	return nil
}

func Dial(ctx context.Context, address string, timeout time.Duration) (*Consumer, error) {
	dialer := net.Dialer{Timeout: timeout, KeepAlive: 30 * time.Second}
	conn, err := dialer.DialContext(ctx, "tcp", address)
	if err != nil {
		return nil, err
	}
	consumer := &Consumer{conn: conn, reader: bufio.NewReader(conn), writer: bufio.NewWriter(conn)}
	if _, err := consumer.writer.WriteString("  V2"); err != nil {
		_ = conn.Close()
		return nil, err
	}
	if err := consumer.writer.Flush(); err != nil {
		_ = conn.Close()
		return nil, err
	}
	return consumer, nil
}

func (c *Consumer) Identify(options IdentifyOptions) error {
	if options.ClientID == "" {
		options.ClientID = "distributed-workbench"
	}
	if options.Hostname == "" {
		options.Hostname, _ = os.Hostname()
	}
	if options.HeartbeatInterval == 0 {
		options.HeartbeatInterval = 30_000
	}
	if options.OutputBufferTime == 0 {
		options.OutputBufferTime = 250
	}
	body, err := json.Marshal(options)
	if err != nil {
		return err
	}
	if err := c.writeBodyCommand("IDENTIFY", body); err != nil {
		return err
	}
	frame, err := ReadFrame(c.reader)
	if err != nil {
		return err
	}
	if frame.Type == FrameError {
		return fmt.Errorf("NSQ IDENTIFY error: %s", frame.Data)
	}
	if frame.Type != FrameResponse {
		return fmt.Errorf("unexpected IDENTIFY frame type %d", frame.Type)
	}
	return nil
}

func (c *Consumer) Subscribe(topic, channel string) error {
	if err := ValidateName(topic); err != nil {
		return err
	}
	if err := ValidateName(channel); err != nil {
		return err
	}
	return c.writeLine(fmt.Sprintf("SUB %s %s", topic, channel))
}

func (c *Consumer) Ready(count int) error {
	if count < 0 {
		return errors.New("RDY count cannot be negative")
	}
	return c.writeLine(fmt.Sprintf("RDY %d", count))
}

func (c *Consumer) Next() (Message, error) {
	for {
		frame, err := ReadFrame(c.reader)
		if err != nil {
			return Message{}, err
		}
		switch frame.Type {
		case FrameResponse:
			if bytes.Equal(frame.Data, []byte("_heartbeat_")) {
				if err := c.writeLine("NOP"); err != nil {
					return Message{}, err
				}
			}
			continue
		case FrameError:
			return Message{}, fmt.Errorf("NSQ error frame: %s", frame.Data)
		case FrameMessage:
			return ParseMessage(frame.Data)
		default:
			return Message{}, fmt.Errorf("unknown NSQ frame type %d", frame.Type)
		}
	}
}

func (c *Consumer) Finish(messageID string) error {
	if len(messageID) != 16 {
		return errors.New("message id must be 16 bytes")
	}
	return c.writeLine("FIN " + messageID)
}

func (c *Consumer) Requeue(messageID string, delay time.Duration) error {
	if len(messageID) != 16 {
		return errors.New("message id must be 16 bytes")
	}
	milliseconds := delay.Milliseconds()
	if milliseconds < 0 {
		milliseconds = 0
	}
	return c.writeLine(fmt.Sprintf("REQ %s %d", messageID, milliseconds))
}

func (c *Consumer) Close() error {
	if c == nil || c.conn == nil {
		return nil
	}
	_ = c.writeLine("CLS")
	return c.conn.Close()
}

func (c *Consumer) writeLine(command string) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	if _, err := c.writer.WriteString(command + "\n"); err != nil {
		return err
	}
	return c.writer.Flush()
}

func (c *Consumer) writeBodyCommand(command string, body []byte) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	if _, err := c.writer.WriteString(command + "\n"); err != nil {
		return err
	}
	if err := binary.Write(c.writer, binary.BigEndian, uint32(len(body))); err != nil {
		return err
	}
	if _, err := c.writer.Write(body); err != nil {
		return err
	}
	return c.writer.Flush()
}

func ReadFrame(reader io.Reader) (Frame, error) {
	var size uint32
	if err := binary.Read(reader, binary.BigEndian, &size); err != nil {
		return Frame{}, err
	}
	if size < 4 || size > maxFrameSize {
		return Frame{}, fmt.Errorf("invalid NSQ frame size %d", size)
	}
	payload := make([]byte, size)
	if _, err := io.ReadFull(reader, payload); err != nil {
		return Frame{}, err
	}
	return Frame{Type: int32(binary.BigEndian.Uint32(payload[:4])), Data: payload[4:]}, nil
}

func ParseMessage(data []byte) (Message, error) {
	if len(data) < 26 {
		return Message{}, errors.New("NSQ message frame is shorter than 26 bytes")
	}
	return Message{
		Timestamp: int64(binary.BigEndian.Uint64(data[:8])),
		Attempts:  binary.BigEndian.Uint16(data[8:10]),
		ID:        string(data[10:26]),
		Body:      append([]byte(nil), data[26:]...),
	}, nil
}

func PublishHTTP(ctx context.Context, client *http.Client, baseURL, topic string, body []byte) error {
	if err := ValidateName(topic); err != nil {
		return err
	}
	if client == nil {
		client = &http.Client{Timeout: 5 * time.Second}
	}
	parsed, err := url.Parse(strings.TrimRight(baseURL, "/") + "/pub")
	if err != nil {
		return err
	}
	query := parsed.Query()
	query.Set("topic", topic)
	parsed.RawQuery = query.Encode()
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, parsed.String(), bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/octet-stream")
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	responseBody, _ := io.ReadAll(io.LimitReader(resp.Body, 4096))
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("NSQ publish failed: HTTP %d: %s", resp.StatusCode, strings.TrimSpace(string(responseBody)))
	}
	if strings.TrimSpace(string(responseBody)) != "OK" {
		return fmt.Errorf("unexpected NSQ publish response: %q", strings.TrimSpace(string(responseBody)))
	}
	return nil
}
