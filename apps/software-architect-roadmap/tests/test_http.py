import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from architect_lab.server import make_server
from architect_lab.networking import dns_roundtrip, tcp_roundtrip, https_roundtrip, recv_exact
import shutil
import socket


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server = make_server('127.0.0.1', 0, Path(self.temp.name) / 'orders.db')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()
        self.temp.cleanup()

    def request(self, body, key='demo', content_type='application/json'):
        data = json.dumps(body).encode()
        request = Request(self.base + '/orders', data=data,
                          headers={'Content-Type': content_type, 'Idempotency-Key': key})
        try: response = urlopen(request, timeout=3)
        except HTTPError as error: response = error
        with response:
            return response.status, json.load(response)

    def test_order_retry_conflict_and_view(self):
        body = {'items': [{'sku': 'book', 'quantity': 2}, {'sku': 'pen', 'quantity': 3}]}
        status, first = self.request(body)
        self.assertEqual((status, first['total']), (201, 3000))
        status, second = self.request(body)
        self.assertEqual((status, second['id']), (200, first['id']))
        self.assertEqual(self.request({'items': [{'sku': 'book', 'quantity': 3}]})[0], 409)
        with urlopen(self.base, timeout=3) as response:
            self.assertIn(first['id'], response.read().decode())
            self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_reject_invalid_input_before_persisting(self):
        for body in [[], {}, {'items': []}, {'items': [None]}, {'items': [{'sku': 'unknown', 'quantity': 1}]},
                     {'items': [{'sku': [], 'quantity': 1}]}, {'items': [{'sku': 'book', 'quantity': True}]},
                     {'items': [{'sku': 'book', 'quantity': 1, 'unit_price': 0}]}]:
            with self.subTest(body=body): self.assertEqual(self.request(body)[0], 400)
        self.assertEqual(self.request({'items': []}, content_type='text/plain')[0], 415)
        with urlopen(self.base + '/orders', timeout=3) as response: self.assertEqual(json.load(response), [])

    def test_two_real_http_services_and_catalog_failure(self):
        with make_server('127.0.0.1', 0, Path(self.temp.name) / 'catalog.db') as catalog:
            thread = threading.Thread(target=catalog.serve_forever, daemon=True)
            thread.start()
            with make_server('127.0.0.1', 0, Path(self.temp.name) / 'consumer.db',
                             f'http://127.0.0.1:{catalog.server_port}') as orders:
                order_thread = threading.Thread(target=orders.serve_forever, daemon=True)
                order_thread.start()
                old_base = self.base
                self.base = f'http://127.0.0.1:{orders.server_port}'
                try:
                    self.assertEqual(self.request({'items': [{'sku': 'book', 'quantity': 1}]})[0], 201)
                    catalog.shutdown()
                    thread.join(timeout=3)
                    catalog.server_close()
                    self.assertEqual(self.request({'items': [{'sku': 'book', 'quantity': 1}]})[0], 200)
                    self.assertEqual(self.request({'items': [{'sku': 'book', 'quantity': 1}]}, 'other')[0], 503)
                finally:
                    self.base = old_base
                    orders.shutdown()
                    order_thread.join(timeout=3)
                    if thread.is_alive():
                        catalog.shutdown()
                        thread.join(timeout=3)


class NetworkTests(unittest.TestCase):
    def test_dns_packet_roundtrip(self):
        self.assertEqual(dns_roundtrip()['A'], '127.0.0.1')

    def test_tcp_framing(self):
        self.assertEqual(tcp_roundtrip()['echo'], 'hello')
        one, two = socket.socketpair()
        with one, two:
            one.sendall(b'xx')
            one.shutdown(socket.SHUT_WR)
            with self.assertRaises(EOFError): recv_exact(two, 4)

    @unittest.skipUnless(shutil.which('openssl'), 'OpenSSL CLI is needed for temporary certificate generation')
    def test_https_verifies_certificate_and_hostname(self):
        self.assertEqual(https_roundtrip(), {'https': {'status': 'ok'}, 'wrong_hostname_rejected': True})


if __name__ == '__main__': unittest.main()
