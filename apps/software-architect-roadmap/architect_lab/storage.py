"""SQLite adapter: atomic order/outbox writes and atomic inbox/projection writes."""
from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import json
import sqlite3
import uuid

from .domain import Line, total

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
 id TEXT PRIMARY KEY, request_key TEXT NOT NULL UNIQUE,
 fingerprint TEXT NOT NULL, total INTEGER NOT NULL CHECK(total >= 0),
 payload TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS outbox (
 event_id TEXT PRIMARY KEY, order_id TEXT NOT NULL REFERENCES orders(id),
 payload TEXT NOT NULL, delivered INTEGER NOT NULL DEFAULT 0 CHECK(delivered IN (0,1))
);
CREATE TABLE IF NOT EXISTS inbox (
 consumer TEXT NOT NULL, event_id TEXT NOT NULL,
 PRIMARY KEY (consumer, event_id)
);
CREATE TABLE IF NOT EXISTS revenue (
 consumer TEXT PRIMARY KEY, amount INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY);
"""


class Conflict(ValueError):
    pass


def request_fingerprint(items):
    raw = json.dumps(items, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


class SqliteOrders:
    def __init__(self, path):
        self.path = str(path)
        with self.connection() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def place(self, key, lines, *, fail_after_insert=False):
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ValueError("Idempotency-Key must contain 1..128 characters")
        amount = total(lines)
        payload = json.dumps([asdict(line) for line in lines], sort_keys=True, separators=(",", ":"))
        fingerprint = request_fingerprint([{"sku": line.sku, "quantity": line.quantity} for line in lines])
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            old = conn.execute("SELECT * FROM orders WHERE request_key = ?", (key,)).fetchone()
            if old:
                if old["fingerprint"] != fingerprint:
                    raise Conflict("the key was already used with a different request")
                return {"id": old["id"], "total": old["total"], "replayed": True}
            order_id, event_id = str(uuid.uuid4()), str(uuid.uuid4())
            conn.execute("INSERT INTO orders(id,request_key,fingerprint,total,payload) VALUES(?,?,?,?,?)",
                         (order_id, key, fingerprint, amount, payload))
            if fail_after_insert:
                raise RuntimeError("injected failure before outbox insert")
            event = json.dumps({"event_id": event_id, "type": "OrderPlaced", "version": 1,
                                "order_id": order_id, "total": amount})
            conn.execute("INSERT INTO outbox(event_id,order_id,payload) VALUES(?,?,?)",
                         (event_id, order_id, event))
        return {"id": order_id, "total": amount, "replayed": False}

    def lookup_request(self, key, items):
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ValueError("Idempotency-Key must contain 1..128 characters")
        with self.connection() as conn:
            old = conn.execute("SELECT * FROM orders WHERE request_key=?", (key,)).fetchone()
            if not old:
                return None
            if old["fingerprint"] != request_fingerprint(items):
                raise Conflict("the key was already used with a different request")
            return {"id": old["id"], "total": old["total"], "replayed": True}

    def list_orders(self):
        with self.connection() as conn:
            return [dict(row) for row in conn.execute("SELECT id,total,created_at FROM orders ORDER BY rowid")]

    def pending(self):
        with self.connection() as conn:
            return [json.loads(row[0]) for row in conn.execute("SELECT payload FROM outbox WHERE delivered=0 ORDER BY rowid")]

    def consume(self, consumer, event, *, fail_after_inbox=False):
        if event.get("type") != "OrderPlaced" or event.get("version") != 1:
            raise ValueError("unsupported event")
        if type(event.get("total")) is not int or event["total"] < 0:
            raise ValueError("invalid amount")
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            inserted = conn.execute("INSERT OR IGNORE INTO inbox VALUES(?,?)", (consumer, event["event_id"])).rowcount
            if not inserted:
                return False
            if fail_after_inbox:
                raise RuntimeError("injected failure before projection update")
            conn.execute("INSERT INTO revenue VALUES(?,?) ON CONFLICT(consumer) DO UPDATE SET amount=amount+excluded.amount",
                         (consumer, event["total"]))
        return True

    def dispatch(self, *, fail_after_consume=False):
        for event in self.pending():
            for consumer in ("analytics", "billing-report"):
                self.consume(consumer, event)
            if fail_after_consume:
                raise RuntimeError("injected crash before delivery acknowledgement")
            with self.connection() as conn:
                conn.execute("UPDATE outbox SET delivered=1 WHERE event_id=?", (event["event_id"],))

    def revenues(self):
        with self.connection() as conn:
            return dict(conn.execute("SELECT consumer, amount FROM revenue"))

    def migrate(self):
        """Expand first. The old query remains valid after the nullable column is added."""
        with self.connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            if not conn.execute("SELECT 1 FROM schema_version WHERE version=1").fetchone():
                conn.execute("ALTER TABLE orders ADD COLUMN currency TEXT")
                conn.execute("UPDATE orders SET currency='JPY' WHERE currency IS NULL")
                conn.execute("INSERT INTO schema_version VALUES(1)")


class MemoryOrders:
    """Single-threaded test adapter; no durability or outbox guarantee."""
    def __init__(self):
        self.orders = {}

    def place(self, key, lines, *, fail_after_insert=False):
        amount = total(lines)
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ValueError("invalid key")
        if key in self.orders:
            previous, result = self.orders[key]
            if [(x.sku, x.quantity) for x in previous] != [(x.sku, x.quantity) for x in lines]:
                raise Conflict("key conflict")
            return {**result, "replayed": True}
        if fail_after_insert:
            raise RuntimeError("injected failure")
        result = {"id": str(uuid.uuid4()), "total": amount, "replayed": False}
        self.orders[key] = (list(lines), result)
        return result
