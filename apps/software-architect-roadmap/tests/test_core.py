import concurrent.futures
import json
from pathlib import Path
import tempfile
import unittest

from architect_lab.domain import Line, total, place_order
from architect_lab.storage import SqliteOrders, MemoryOrders, Conflict
from architect_lab.distributed import PartitionedRegister, HashRing, EventLog, TokenBucket, tumbling_windows
from architect_lab.data import ObjectStore, DocumentStore, analytics
from architect_lab.planning import critical_path, pert, validate_raci, weighted_decision
from architect_lab.gof import run_all


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = SqliteOrders(Path(self.temp.name) / "orders.db")
        self.lines = [Line("book", 2, 1200), Line("pen", 3, 200)]

    def test_money_and_invalid_quantities(self):
        self.assertEqual(total(self.lines), 3000)
        for quantity in [0, -1, True, 1.5, 1001, "1"]:
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                Line("book", quantity, 1200)
        with self.assertRaises(ValueError): total([])
        with self.assertRaises(ValueError): Line("book", 1, -1)

    def test_port_contract_on_both_adapters(self):
        for repo in [self.repo, MemoryOrders()]:
            with self.subTest(adapter=type(repo).__name__):
                first = place_order(repo, "key", self.lines)
                again = place_order(repo, "key", self.lines)
                self.assertEqual(first["id"], again["id"])
                self.assertTrue(again["replayed"])
                with self.assertRaises(Conflict):
                    place_order(repo, "key", [Line("book", 3, 1200)])

    def test_rollback_and_reopen(self):
        with self.assertRaises(RuntimeError):
            self.repo.place("key", self.lines, fail_after_insert=True)
        reopened = SqliteOrders(self.repo.path)
        self.assertEqual(reopened.list_orders(), [])
        self.assertEqual(reopened.pending(), [])
        self.repo.place("key", self.lines)
        self.assertEqual(len(reopened.list_orders()), 1)
        self.assertEqual(len(reopened.pending()), 1)

    def test_retry_retains_original_price_after_catalog_change(self):
        for repo in [self.repo, MemoryOrders()]:
            first = repo.place("price-key", [Line("book", 1, 1200)])
            retry = repo.place("price-key", [Line("book", 1, 1400)])
            self.assertEqual(retry["total"], 1200)
            self.assertEqual(retry["id"], first["id"])

    def test_concurrent_retries_create_one_order(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.repo.place("same", self.lines), range(24)))
        self.assertEqual(len({r["id"] for r in results}), 1)
        self.assertEqual(sum(not r["replayed"] for r in results), 1)
        self.assertEqual(len(self.repo.pending()), 1)

    def test_crash_after_side_effect_does_not_double_count(self):
        self.repo.place("key", self.lines)
        with self.assertRaises(RuntimeError): self.repo.dispatch(fail_after_consume=True)
        reopened = SqliteOrders(self.repo.path)
        reopened.dispatch()
        reopened.dispatch()
        self.assertEqual(reopened.revenues(), {"analytics": 3000, "billing-report": 3000})
        self.assertEqual(reopened.pending(), [])

    def test_consumer_inbox_rolls_back_with_projection(self):
        self.repo.place("key", self.lines)
        event = self.repo.pending()[0]
        with self.assertRaises(RuntimeError):
            self.repo.consume("new", event, fail_after_inbox=True)
        self.assertTrue(self.repo.consume("new", event))
        self.assertEqual(self.repo.revenues()["new"], 3000)
        self.assertFalse(self.repo.consume("new", event))

    def test_repeated_migration_preserves_old_query(self):
        self.repo.place("key", self.lines)
        before = self.repo.list_orders()
        self.repo.migrate()
        self.repo.migrate()
        self.assertEqual(self.repo.list_orders(), before)
        with self.repo.connection() as connection:
            self.assertEqual(connection.execute("SELECT currency FROM orders").fetchone()[0], "JPY")
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0], 1)


class DistributedTests(unittest.TestCase):
    def test_cap_partition_and_healing(self):
        for mode in ["CP", "AP"]:
            register = PartitionedRegister(mode)
            register.partitioned = True
            register.write(42)
            if mode == "CP":
                with self.assertRaises(ConnectionError): register.read("isolated")
            else:
                self.assertEqual(register.read("isolated"), 0)
            register.heal()
            self.assertEqual(register.read("isolated"), 42)

    def test_ring_moves_keys_only_to_new_node(self):
        before, after = HashRing(["a", "b", "c"]), HashRing(["a", "b", "c", "d"])
        moved = [str(i) for i in range(1000) if before.owner(str(i)) != after.owner(str(i))]
        self.assertTrue(100 < len(moved) < 500)
        self.assertTrue(all(after.owner(key) == "d" for key in moved))

    def test_consumer_offsets_are_independent_and_replayable(self):
        log = EventLog()
        log.publish({"amount": 10})
        self.assertEqual(log.poll("a"), log.poll("a"))
        log.commit("a", 1)
        self.assertEqual(log.poll("a"), [])
        self.assertEqual(len(log.poll("b")), 1)
        with self.assertRaises(ValueError): log.commit("a", 0)

    def test_rate_limit_and_refill(self):
        bucket = TokenBucket(2, 1)
        self.assertEqual([bucket.allow(t) for t in [0, 0, 0, 0.5, 1]], [True, True, False, False, True])
        with self.assertRaises(ValueError): bucket.allow(0)

    def test_watermark_accepts_out_of_order_and_drops_closed_window(self):
        events = [{"time": t, "sku": "book", "quantity": 1} for t in [1, 61, 58, 130, 2]]
        buckets, late = tumbling_windows(events)
        self.assertEqual(buckets, {(0, "book"): 2, (60, "book"): 1, (120, "book"): 1})
        self.assertEqual([x["time"] for x in late], [2])


class DataAndPlanningTests(unittest.TestCase):
    def test_object_integrity_and_path_validation(self):
        with tempfile.TemporaryDirectory() as root:
            store = ObjectStore(root)
            key = store.put(b"original")
            self.assertEqual(store.put(b"original"), key)
            self.assertEqual(store.get(key), b"original")
            with self.assertRaises(ValueError): store.get("../secret")
            Path(root, key).write_bytes(b"corrupt")
            with self.assertRaises(ValueError): store.get(key)

    def test_document_optimistic_version(self):
        with tempfile.TemporaryDirectory() as root:
            store = DocumentStore(root)
            version = store.put("id", {"value": 1})
            store.put("id", {"value": 2}, version)
            with self.assertRaises(ValueError): store.put("id", {"value": 3}, version)
            self.assertEqual(store.get("id"), {"value": 2})

    def test_analytical_totals(self):
        self.assertEqual(analytics()["revenue"], {"learning": 3600, "stationery": 600, "ALL": 4200})

    def test_schedule_parallel_work_and_cycle(self):
        tasks = {"schema": (2, []), "api": (3, ["schema"]), "ui": (2, ["schema"]), "release": (1, ["api", "ui"])}
        self.assertEqual(critical_path(tasks), {"duration": 6, "path": ["schema", "api", "release"]})
        with self.assertRaises(ValueError): critical_path({"a": (1, ["b"]), "b": (1, ["a"])})
        self.assertAlmostEqual(pert(2, 4, 8), 26 / 6)
        with self.assertRaises(ValueError): pert(3, 2, 1)

    def test_decision_changes_when_weights_change(self):
        scores = {"simple": {"cost": 5, "scale": 1}, "scaled": {"cost": 1, "scale": 5}}
        self.assertEqual(weighted_decision({"cost": 3, "scale": 1}, scores)[0][0], "simple")
        self.assertEqual(weighted_decision({"cost": 1, "scale": 3}, scores)[0][0], "scaled")
        with self.assertRaises(ValueError): validate_raci({"release": {"x": "A", "y": "A"}})

    def test_all_gof_examples_have_expected_behavior(self):
        result = run_all()
        self.assertEqual(len(result), 23)
        expected = {
            "factory_method": '{"total": 3000}', "abstract_factory": [[1, 2], [1, 2]],
            "builder": ("SELECT * FROM orders WHERE total >= ?", (1000,)),
            "prototype": [1, 2], "singleton": True, "adapter": 1200,
            "bridge": ['{"revenue": 3000}', 'revenue: 3000'], "composite": 1600,
            "decorator": 1500, "facade": ['reserve:book', 'charge:1200'],
            "flyweight": {"shared": True, "quantities": [1, 3]},
            "proxy": {"prices": [1200, 1200], "origin_calls": 1},
            "chain_of_responsibility": ['401', '400', 'accepted'], "command": [['book'], []],
            "interpreter": [False, True], "iterator": [1, 2, 3],
            "mediator": ['inventory:reserve', 'billing:charge'], "memento": 'draft',
            "observer": ['analytics:OrderPlaced', 'billing:OrderPlaced'],
            "state": {"state": 'Shipped', "early_ship_rejected": True},
            "strategy": [1000, 900], "template_method": [6, 6], "visitor": [100, 80]
        }
        for name, value in expected.items():
            with self.subTest(pattern=name): self.assertEqual(result[name], value)


if __name__ == '__main__': unittest.main()
