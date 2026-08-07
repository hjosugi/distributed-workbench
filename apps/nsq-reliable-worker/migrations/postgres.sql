-- Production replacement for the JSONL sample stores.

CREATE TABLE IF NOT EXISTS job_outbox (
    job_id text PRIMARY KEY,
    topic text NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    published_at timestamptz,
    publish_attempts integer NOT NULL DEFAULT 0,
    last_error text
);

CREATE INDEX IF NOT EXISTS job_outbox_pending_idx
    ON job_outbox (created_at)
    WHERE published_at IS NULL;

CREATE TABLE IF NOT EXISTS processed_messages (
    consumer_name text NOT NULL,
    job_id text NOT NULL,
    nsq_message_id text NOT NULL,
    attempts integer NOT NULL,
    processed_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (consumer_name, job_id)
);

CREATE TABLE IF NOT EXISTS dead_letters (
    id bigserial PRIMARY KEY,
    source_topic text NOT NULL,
    source_channel text NOT NULL,
    job_id text,
    nsq_message_id text NOT NULL,
    attempts integer NOT NULL,
    reason text NOT NULL,
    payload jsonb NOT NULL,
    failed_at timestamptz NOT NULL DEFAULT now(),
    replayed_at timestamptz
);

-- Transactional outbox example:
-- BEGIN;
-- INSERT INTO business_table (...);
-- INSERT INTO job_outbox(job_id, topic, payload) VALUES (...);
-- COMMIT;

-- Idempotent consumer example:
-- BEGIN;
-- INSERT INTO processed_messages(consumer_name, job_id, nsq_message_id, attempts)
-- VALUES ('processor', $1, $2, $3)
-- ON CONFLICT DO NOTHING;
-- Apply the business effect only when the insert affected one row.
-- COMMIT;
