import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PRODUCTS = [{"sku": "book", "unit_price": 1200}, {"sku": "pen", "unit_price": 200}]

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body):
        raw = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/products': self.send(200, PRODUCTS)
        elif path == '/health': self.send(200, {'status': 'ok'})
        else: self.send(404, {'error': 'not found'})
    def do_POST(self): self.send(405, {'error': 'method not allowed'})

if __name__ == '__main__':
    with ThreadingHTTPServer((os.getenv('BIND_HOST', '127.0.0.1'), int(os.getenv('PORT', '8081'))), Handler) as server:
        server.serve_forever()
