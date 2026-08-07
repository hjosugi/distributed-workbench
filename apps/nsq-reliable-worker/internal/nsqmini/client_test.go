package nsqmini

import (
	"bufio"
	"bytes"
	"context"
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"testing"
	"time"
)

func TestReadFrameAndParseMessage(t *testing.T) {
	t.Parallel()
	messageData := make([]byte, 0, 40)
	timestamp := make([]byte, 8)
	binary.BigEndian.PutUint64(timestamp, 123)
	messageData = append(messageData, timestamp...)
	attempts := make([]byte, 2)
	binary.BigEndian.PutUint16(attempts, 3)
	messageData = append(messageData, attempts...)
	messageData = append(messageData, []byte("0123456789abcdef")...)
	messageData = append(messageData, []byte(`{"hello":"world"}`)...)

	var wire bytes.Buffer
	_ = binary.Write(&wire, binary.BigEndian, uint32(4+len(messageData)))
	_ = binary.Write(&wire, binary.BigEndian, uint32(FrameMessage))
	_, _ = wire.Write(messageData)

	frame, err := ReadFrame(&wire)
	if err != nil {
		t.Fatal(err)
	}
	message, err := ParseMessage(frame.Data)
	if err != nil {
		t.Fatal(err)
	}
	if message.ID != "0123456789abcdef" || message.Attempts != 3 || message.Timestamp != 123 {
		t.Fatalf("unexpected message: %+v", message)
	}
}

func TestValidateName(t *testing.T) {
	t.Parallel()
	for _, value := range []string{"jobs", "jobs.v2", "temp#ephemeral"} {
		if err := ValidateName(value); err != nil {
			t.Fatalf("expected %q to be valid: %v", value, err)
		}
	}
	for _, value := range []string{"", "contains space", "slash/name"} {
		if err := ValidateName(value); err == nil {
			t.Fatalf("expected %q to be invalid", value)
		}
	}
}

func TestConsumerProtocolFlow(t *testing.T) {
	t.Parallel()
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()

	serverErr := make(chan error, 1)
	go func() {
		conn, acceptErr := listener.Accept()
		if acceptErr != nil {
			serverErr <- acceptErr
			return
		}
		defer conn.Close()
		reader := bufio.NewReader(conn)
		magic := make([]byte, 4)
		if _, err := io.ReadFull(reader, magic); err != nil {
			serverErr <- err
			return
		}
		if string(magic) != "  V2" {
			serverErr <- fmt.Errorf("unexpected magic %q", magic)
			return
		}
		line, err := reader.ReadString('\n')
		if err != nil || line != "IDENTIFY\n" {
			serverErr <- fmt.Errorf("unexpected identify command %q: %v", line, err)
			return
		}
		var bodySize uint32
		if err := binary.Read(reader, binary.BigEndian, &bodySize); err != nil {
			serverErr <- err
			return
		}
		body := make([]byte, bodySize)
		if _, err := io.ReadFull(reader, body); err != nil {
			serverErr <- err
			return
		}
		if !bytes.Contains(body, []byte(`"feature_negotiation":true`)) {
			serverErr <- fmt.Errorf("identify body missing feature negotiation: %s", body)
			return
		}
		if err := writeTestFrame(conn, FrameResponse, []byte(`{"max_rdy_count":2500}`)); err != nil {
			serverErr <- err
			return
		}
		for _, expected := range []string{"SUB jobs processor\n", "RDY 1\n"} {
			line, err = reader.ReadString('\n')
			if err != nil || line != expected {
				serverErr <- fmt.Errorf("expected %q, got %q: %v", expected, line, err)
				return
			}
		}
		if err := writeTestFrame(conn, FrameResponse, []byte("_heartbeat_")); err != nil {
			serverErr <- err
			return
		}
		line, err = reader.ReadString('\n')
		if err != nil || line != "NOP\n" {
			serverErr <- fmt.Errorf("expected NOP, got %q: %v", line, err)
			return
		}
		messageData := make([]byte, 26)
		binary.BigEndian.PutUint64(messageData[:8], 456)
		binary.BigEndian.PutUint16(messageData[8:10], 1)
		copy(messageData[10:26], []byte("fedcba9876543210"))
		messageData = append(messageData, []byte(`{"id":"job"}`)...)
		if err := writeTestFrame(conn, FrameMessage, messageData); err != nil {
			serverErr <- err
			return
		}
		line, err = reader.ReadString('\n')
		if err != nil || line != "FIN fedcba9876543210\n" {
			serverErr <- fmt.Errorf("expected FIN, got %q: %v", line, err)
			return
		}
		serverErr <- nil
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	consumer, err := Dial(ctx, listener.Addr().String(), time.Second)
	if err != nil {
		t.Fatal(err)
	}
	defer consumer.Close()
	if err := consumer.Identify(IdentifyOptions{FeatureNegotiation: true}); err != nil {
		t.Fatal(err)
	}
	if err := consumer.Subscribe("jobs", "processor"); err != nil {
		t.Fatal(err)
	}
	if err := consumer.Ready(1); err != nil {
		t.Fatal(err)
	}
	message, err := consumer.Next()
	if err != nil {
		t.Fatal(err)
	}
	if message.ID != "fedcba9876543210" || message.Attempts != 1 {
		t.Fatalf("unexpected message: %+v", message)
	}
	if err := consumer.Finish(message.ID); err != nil {
		t.Fatal(err)
	}
	if err := <-serverErr; err != nil {
		t.Fatal(err)
	}
}

func writeTestFrame(writer io.Writer, frameType int32, data []byte) error {
	if err := binary.Write(writer, binary.BigEndian, uint32(4+len(data))); err != nil {
		return err
	}
	if err := binary.Write(writer, binary.BigEndian, uint32(frameType)); err != nil {
		return err
	}
	_, err := writer.Write(data)
	return err
}
