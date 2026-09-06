"""Deterministic models, not a production consensus or messaging implementation."""
from collections import defaultdict
import hashlib
from bisect import bisect_left


class PartitionedRegister:
    def __init__(self, mode):
        if mode not in {"CP", "AP"}:
            raise ValueError("mode must be CP or AP")
        self.mode = mode
        self.values = {"leader": 0, "isolated": 0}
        self.partitioned = False

    def write(self, value):
        self.values["leader"] = value
        if not self.partitioned:
            self.values["isolated"] = value

    def read(self, node):
        if self.partitioned and node == "isolated" and self.mode == "CP":
            raise ConnectionError("cannot reach leader; reject read")
        return self.values[node]

    def heal(self):
        self.partitioned = False
        self.values["isolated"] = self.values["leader"]


class HashRing:
    def __init__(self, nodes, virtual_nodes=64):
        if not nodes or virtual_nodes < 1 or len(set(nodes)) != len(nodes):
            raise ValueError("unique nodes and positive virtual_nodes required")
        self.points = sorted((self.hash(f"{node}:{i}"), node) for node in nodes for i in range(virtual_nodes))
        self.keys = [key for key, _ in self.points]

    @staticmethod
    def hash(value):
        return int.from_bytes(hashlib.sha256(value.encode()).digest(), "big")

    def owner(self, key):
        index = bisect_left(self.keys, self.hash(key)) % len(self.keys)
        return self.points[index][1]


class TokenBucket:
    def __init__(self, capacity, rate, now=0):
        if capacity <= 0 or rate <= 0:
            raise ValueError("capacity and rate must be positive")
        self.capacity, self.rate = capacity, rate
        self.tokens, self.last = float(capacity), now

    def allow(self, now):
        if now < self.last:
            raise ValueError("clock must be monotonic")
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens < 1:
            return False
        self.tokens -= 1
        return True


class EventLog:
    """In-memory append-only pub/sub model with independent consumer offsets."""
    def __init__(self):
        self.events, self.offsets = [], defaultdict(int)

    def publish(self, event):
        self.events.append(dict(event))

    def poll(self, group, limit=10):
        offset = self.offsets[group]
        return list(enumerate(self.events[offset:offset + limit], start=offset))

    def commit(self, group, next_offset):
        if not self.offsets[group] <= next_offset <= len(self.events):
            raise ValueError("invalid offset")
        self.offsets[group] = next_offset


def tumbling_windows(events, size=60, allowed_lateness=5):
    """Event time; global watermark. Returns final buckets and dropped events."""
    if size <= 0 or allowed_lateness < 0:
        raise ValueError("invalid window configuration")
    max_seen = float("-inf")
    buckets, late = defaultdict(int), []
    for event in events:
        timestamp = event["time"]
        start = timestamp // size * size
        if start + size <= max_seen - allowed_lateness:
            late.append(event)
            continue
        max_seen = max(max_seen, timestamp)
        buckets[(start, event["sku"])] += event["quantity"]
    return dict(buckets), late
