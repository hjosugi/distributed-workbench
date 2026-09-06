import argparse
import json
from pathlib import Path
import secrets
import tempfile

from .domain import Line, place_order
from .storage import SqliteOrders, MemoryOrders
from .distributed import PartitionedRegister, HashRing, EventLog, tumbling_windows, TokenBucket
from .data import analytics, DocumentStore, ObjectStore
from .planning import weighted_decision, pert, critical_path, validate_raci
from .security import sign_token, verify_token, AuthorizationCodes, pkce_challenge, password_record, check_password


def run(name):
    with tempfile.TemporaryDirectory() as temporary:
        repo = SqliteOrders(Path(temporary) / "orders.db")
        lines = [Line("book", 2, 1200), Line("pen", 3, 200)]
        if name == "orders":
            first = place_order(repo, "demo-1", lines)
            replay = place_order(repo, "demo-1", lines)
            memory = place_order(MemoryOrders(), "demo-1", lines)
            return {"first": first, "retry": replay, "memory_adapter_total": memory["total"]}
        if name == "acid":
            try:
                repo.place("failed", lines, fail_after_insert=True)
            except RuntimeError:
                pass
            before = len(repo.list_orders())
            repo.place("success", lines)
            reopened = SqliteOrders(repo.path)
            return {"rows_after_failure": before, "rows_after_reopen": len(reopened.list_orders()), "outbox": len(reopened.pending())}
        if name == "events":
            repo.place("demo", lines)
            try:
                repo.dispatch(fail_after_consume=True)
            except RuntimeError:
                pass
            repo.dispatch()
            log = EventLog()
            log.publish({"type": "OrderPlaced"})
            log.commit("analytics", 1)
            return {"revenue_after_retry": repo.revenues(), "analytics_pending": log.poll("analytics"),
                    "billing_pending": log.poll("billing")}
        if name == "cap":
            results = {}
            for mode in ("CP", "AP"):
                register = PartitionedRegister(mode)
                register.partitioned = True
                register.write(42)
                try:
                    results[mode] = register.read("isolated")
                except ConnectionError:
                    results[mode] = "unavailable"
                register.heal()
                results[mode + "_after_heal"] = register.read("isolated")
            return results
        if name == "distributed":
            old, new = HashRing(["a", "b", "c"]), HashRing(["a", "b", "c", "d"])
            moved = sum(old.owner(str(i)) != new.owner(str(i)) for i in range(1000))
            bucket = TokenBucket(2, 1)
            return {"moved_of_1000": moved, "admitted_at_0_0_0_1": [bucket.allow(t) for t in [0, 0, 0, 1]]}
        if name == "data":
            documents = DocumentStore(Path(temporary) / "documents")
            version = documents.put("profile-1", {"name": "demo", "interests": ["books"]})
            objects = ObjectStore(Path(temporary) / "objects")
            key = objects.put(b"order export")
            return {**analytics(), "document": documents.get("profile-1"), "version": version,
                    "object": objects.get(key).decode()}
        if name == "streaming":
            events = [{"time": t, "sku": "book", "quantity": 1} for t in [1, 61, 58, 130, 2]]
            buckets, late = tumbling_windows(events)
            return {"windows": [{"start": k[0], "sku": k[1], "quantity": v} for k, v in sorted(buckets.items())], "late": late}
        if name == "migration":
            repo.place("demo", lines)
            repo.migrate()
            repo.migrate()
            with repo.connection() as conn:
                return {"currencies": [x[0] for x in conn.execute("SELECT currency FROM orders")],
                        "versions": [x[0] for x in conn.execute("SELECT version FROM schema_version")]}
        if name == "security":
            key = secrets.token_bytes(32)
            token = sign_token({"iss": "lab", "aud": "orders", "sub": "demo", "exp": 200}, key)
            claims = verify_token(token, key, issuer="lab", audience="orders", now=100)
            verifier = secrets.token_urlsafe(48)
            codes = AuthorizationCodes()
            uri = "http://127.0.0.1:8090/callback"
            code = codes.authorize("local-client", uri, pkce_challenge(verifier), "demo", 100)
            grant = codes.exchange(code, "local-client", uri, verifier, 101)
            record = password_record("demo password")
            return {"claims": claims, "grant": grant, "password_ok": check_password("demo password", record),
                    "wrong_password_ok": check_password("wrong", record)}
        if name == "planning":
            ranking = weighted_decision({"simplicity": 3, "scale": 1}, {
                "modular-monolith": {"simplicity": 5, "scale": 3},
                "microservices": {"simplicity": 2, "scale": 5}})
            return {"ranking": ranking, "expected_days": pert(2, 4, 8),
                    "schedule": critical_path({"schema": (2, []), "api": (3, ["schema"]),
                                               "ui": (2, ["schema"]), "release": (1, ["api", "ui"])}),
                    "raci_valid": validate_raci({"release": {"lead": "A", "engineer": "R", "product": "C"}})}
        if name == "gof":
            from .gof import run_all
            return run_all()
        raise ValueError(name)


LABS = ["orders", "acid", "events", "cap", "distributed", "data", "streaming", "migration", "security", "planning", "gof"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lab", choices=LABS + ["all"])
    args = parser.parse_args()
    selected = LABS if args.lab == "all" else [args.lab]
    print(json.dumps({name: run(name) for name in selected}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
