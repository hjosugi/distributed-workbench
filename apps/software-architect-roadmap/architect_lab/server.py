"""Local HTTP adapter. Bind to loopback unless explicitly configured for a container."""
import argparse
import html
import json
import os
from pathlib import Path
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from urllib.request import urlopen
from urllib.error import URLError

from .domain import Line, place_order
from .storage import Conflict, SqliteOrders

PRODUCTS = [{"sku": "book", "unit_price": 1200}, {"sku": "pen", "unit_price": 200}]


def make_server(host="127.0.0.1", port=8080, db="orders.db", catalog_url=None):
    repository = SqliteOrders(db)

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, fmt, *args):
            print(json.dumps({"timestamp": time.time(), "service": "orders",
                              "message": fmt % args}), file=sys.stderr, flush=True)

        def reply(self, status, body, content_type="application/json", cache="no-store"):
            raw = (json.dumps(body) if content_type == "application/json" else body).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", cache)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/health":
                return self.reply(200, {"status": "ok"})
            if path == "/products":
                return self.reply(200, PRODUCTS, cache="public, max-age=0, s-maxage=30")
            if path == "/orders":
                return self.reply(200, repository.list_orders())
            if path == "/":
                rows = "".join(f"<tr><td>{html.escape(x['id'])}</td><td>{x['total']}</td></tr>"
                               for x in repository.list_orders())
                return self.reply(200, "<!doctype html><html lang='en'><meta charset='utf-8'>"
                                  "<title>Orders</title><h1>Orders</h1><table><tr><th>ID</th>"
                                  f"<th>JPY</th></tr>{rows}</table></html>", "text/html")
            return self.reply(404, {"error": "not found"})

        def do_POST(self):
            if urlsplit(self.path).path != "/orders":
                return self.reply(404, {"error": "not found"})
            if self.headers.get("Transfer-Encoding"):
                return self.reply(400, {"error": "chunked bodies are not supported in this lab"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self.reply(415, {"error": "application/json required"})
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if length < 0:
                    return self.reply(411, {"error": "Content-Length required"})
                if length > 65536:
                    return self.reply(413, {"error": "body too large"})
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict) or set(payload) != {"items"}:
                    raise ValueError("body must contain items only")
                items = payload["items"]
                if not isinstance(items, list) or not 1 <= len(items) <= 100:
                    raise ValueError("items must contain 1..100 entries")
                for item in items:
                    if not isinstance(item, dict) or set(item) != {"sku", "quantity"}:
                        raise ValueError("each item must contain sku and quantity")
                    if not isinstance(item["sku"], str):
                        raise ValueError("sku must be a string")
                    Line(item["sku"], item["quantity"], 0)
                previous = repository.lookup_request(self.headers.get("Idempotency-Key"), items)
                if previous:
                    return self.reply(200, previous)
                products = PRODUCTS
                if catalog_url:
                    try:
                        with urlopen(catalog_url.rstrip("/") + "/products", timeout=2) as response:
                            products = json.load(response)
                    except (URLError, TimeoutError, ValueError):
                        return self.reply(503, {"error": "catalog unavailable; retry later"})
                prices = {x["sku"]: x["unit_price"] for x in products}
                lines = [Line(x["sku"], x["quantity"], prices[x["sku"]]) for x in items]
                result = place_order(repository, self.headers.get("Idempotency-Key"), lines)
                self.reply(200 if result["replayed"] else 201, result)
            except Conflict as error:
                self.reply(409, {"error": str(error)})
            except (ValueError, KeyError, TypeError) as error:
                self.reply(400, {"error": str(error)})

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.getenv("BIND_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    parser.add_argument("--db", default=os.getenv("ORDER_DB", "orders.db"))
    args = parser.parse_args()
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    with make_server(args.host, args.port, args.db, os.getenv("CATALOG_URL")) as server:
        print(f"Orders: http://{args.host}:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
