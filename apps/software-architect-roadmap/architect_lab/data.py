"""Data models: local document/object adapters and real SQLite analytical queries."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile


class ObjectStore:
    """Immutable content-addressed local objects; not an S3 server."""
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, data):
        key = hashlib.sha256(data).hexdigest()
        fd, temporary = tempfile.mkstemp(dir=self.root)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.root / key)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return key

    def get(self, key):
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("invalid object key")
        raw = (self.root / key).read_bytes()
        if hashlib.sha256(raw).hexdigest() != key:
            raise ValueError("object checksum mismatch")
        return raw


class DocumentStore:
    """Single-process document model using immutable object versions and an in-memory index."""
    def __init__(self, root):
        self.objects, self.index = ObjectStore(root), {}

    def put(self, document_id, document, expected_version=None):
        if self.index.get(document_id) != expected_version:
            raise ValueError("version conflict")
        version = self.objects.put(json.dumps(document, sort_keys=True).encode())
        self.index[document_id] = version
        return version

    def get(self, document_id):
        return json.loads(self.objects.get(self.index[document_id]))


def analytics():
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript("""
        CREATE TABLE products(sku TEXT PRIMARY KEY, category TEXT NOT NULL);
        CREATE TABLE sales(day TEXT, sku TEXT REFERENCES products(sku), quantity INTEGER, amount INTEGER);
        INSERT INTO products VALUES ('book','learning'), ('pen','stationery');
        INSERT INTO sales VALUES ('2026-09-01','book',2,2400), ('2026-09-01','pen',3,600),
                                 ('2026-09-02','book',1,1200);
        CREATE INDEX sales_sku_idx ON sales(sku);
        """)
        rows = connection.execute("""
          SELECT p.category, SUM(s.amount) FROM sales s JOIN products p USING(sku)
          GROUP BY p.category
          UNION ALL SELECT 'ALL', SUM(amount) FROM sales
        """).fetchall()
        plan = connection.execute("EXPLAIN QUERY PLAN SELECT * FROM sales WHERE sku=?", ("book",)).fetchall()
        return {"revenue": dict(rows), "query_plan": plan}
    finally:
        connection.close()
