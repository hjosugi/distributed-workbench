export type Recipe = {
  id: string
  name: string
  description: string
  schema: string
  starter: string
}

export const recipes: Recipe[] = [
  {
    id: 'nsq-reliability',
    name: 'NSQ reliability',
    description: 'Transactional outbox、idempotent consumer、dead letterを試します。',
    schema: `
CREATE TABLE job_outbox (
  job_id text PRIMARY KEY,
  topic text NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz,
  publish_attempts integer NOT NULL DEFAULT 0,
  last_error text
);

CREATE INDEX job_outbox_pending_idx
  ON job_outbox (created_at)
  WHERE published_at IS NULL;

CREATE TABLE processed_messages (
  consumer_name text NOT NULL,
  job_id text NOT NULL,
  nsq_message_id text NOT NULL,
  attempts integer NOT NULL CHECK (attempts > 0),
  processed_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (consumer_name, job_id)
);

CREATE TABLE dead_letters (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source_topic text NOT NULL,
  job_id text,
  attempts integer NOT NULL,
  reason text NOT NULL,
  payload jsonb NOT NULL,
  failed_at timestamptz NOT NULL DEFAULT now(),
  replayed_at timestamptz
);

INSERT INTO job_outbox(job_id, topic, payload) VALUES
  ('job-001', 'jobs', '{"type":"send-email","to":"demo@example.com"}'),
  ('job-002', 'jobs', '{"type":"resize-image","image":"hero.png"}');
`,
    starter: `-- Pending outbox rows are safe to publish more than once.
SELECT job_id, topic, payload, publish_attempts
FROM job_outbox
WHERE published_at IS NULL
ORDER BY created_at;

-- Idempotent consumer gate:
INSERT INTO processed_messages(consumer_name, job_id, nsq_message_id, attempts)
VALUES ('processor', 'job-001', '0123456789abcdef', 1)
ON CONFLICT DO NOTHING
RETURNING *;
`,
  },
  {
    id: 'harbor-observer',
    name: 'Harbor observer history',
    description: '複数Harbor serverのprobe、content hash、divergenceを保存するschemaです。',
    schema: `
CREATE TABLE harbor_servers (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL UNIQUE,
  base_url text NOT NULL UNIQUE,
  enabled boolean NOT NULL DEFAULT true
);

CREATE TABLE probe_runs (
  id uuid PRIMARY KEY,
  path text NOT NULL CHECK (path LIKE '/%'),
  started_at timestamptz NOT NULL,
  finished_at timestamptz NOT NULL,
  state text NOT NULL CHECK (state IN ('healthy','divergent','single-copy-risk','unavailable'))
);

CREATE TABLE probe_results (
  run_id uuid NOT NULL REFERENCES probe_runs(id) ON DELETE CASCADE,
  server_id bigint NOT NULL REFERENCES harbor_servers(id),
  reachable boolean NOT NULL,
  http_status integer,
  latency_ms integer NOT NULL CHECK (latency_ms >= 0),
  body_bytes integer NOT NULL CHECK (body_bytes >= 0),
  sha256 text,
  error text,
  PRIMARY KEY (run_id, server_id)
);

CREATE INDEX probe_results_server_idx ON probe_results(server_id, run_id);

INSERT INTO harbor_servers(name, base_url) VALUES
  ('primary', 'https://server-a.example'),
  ('backup', 'https://server-b.example');
`,
    starter: `SELECT s.name, r.reachable, r.http_status, r.latency_ms, r.sha256
FROM probe_results r
JOIN harbor_servers s ON s.id = r.server_id
ORDER BY r.latency_ms;

-- Detect hash variants within one run.
SELECT run_id, count(DISTINCT sha256) AS variants
FROM probe_results
WHERE reachable
GROUP BY run_id
HAVING count(DISTINCT sha256) > 1;
`,
  },
  {
    id: 'orders-outbox',
    name: 'Orders + transactional outbox',
    description: 'business writeとevent publicationを1 transactionにまとめるpatternです。',
    schema: `
CREATE TABLE orders (
  id uuid PRIMARY KEY,
  customer_email text NOT NULL,
  total_cents integer NOT NULL CHECK (total_cents >= 0),
  status text NOT NULL DEFAULT 'created',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE domain_outbox (
  event_id uuid PRIMARY KEY,
  aggregate_type text NOT NULL,
  aggregate_id uuid NOT NULL,
  event_type text NOT NULL,
  payload jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  published_at timestamptz
);

BEGIN;
INSERT INTO orders(id, customer_email, total_cents)
VALUES ('11111111-1111-1111-1111-111111111111', 'buyer@example.com', 3980);
INSERT INTO domain_outbox(event_id, aggregate_type, aggregate_id, event_type, payload)
VALUES (
  '22222222-2222-2222-2222-222222222222',
  'order',
  '11111111-1111-1111-1111-111111111111',
  'order.created',
  '{"total_cents":3980}'
);
COMMIT;
`,
    starter: `SELECT o.id, o.status, o.total_cents, e.event_type, e.published_at
FROM orders o
JOIN domain_outbox e ON e.aggregate_id = o.id;
`,
  },
  {
    id: 'blank',
    name: 'Blank PostgreSQL',
    description: '空のpublic schemaから自由に試します。',
    schema: '',
    starter: `CREATE TABLE notes (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  body text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO notes(body) VALUES ('PGlite is running in this browser.');
SELECT * FROM notes;
`,
  },
]
