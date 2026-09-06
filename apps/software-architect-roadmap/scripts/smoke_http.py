"""Exercise an already running local order API."""
import json
import sys
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError

base = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8080'
key = str(uuid.uuid4())

def post(quantity):
    request = Request(base + '/orders', data=json.dumps({'items': [{'sku': 'book', 'quantity': quantity}]}).encode(),
                      headers={'Content-Type': 'application/json', 'Idempotency-Key': key})
    try: response = urlopen(request, timeout=5)
    except HTTPError as error: response = error
    with response: return response.status, json.load(response)

first, replay, conflict = post(2), post(2), post(3)
assert first[0] == 201 and first[1]['total'] == 2400, first
assert replay[0] == 200 and replay[1]['id'] == first[1]['id'], replay
assert conflict[0] == 409, conflict
print('PASS: create, retry, conflicting key')
