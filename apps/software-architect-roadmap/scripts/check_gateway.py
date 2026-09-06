"""Verify real NGINX cache behavior after the Compose stack starts."""
from urllib.request import Request, urlopen

base = 'http://127.0.0.1:8088/products'
with urlopen(base, timeout=5) as response:
    first = response.headers.get('X-Cache')
    response.read()
with urlopen(base, timeout=5) as response:
    second = response.headers.get('X-Cache')
    response.read()
assert first in {'MISS', 'HIT'} and second == 'HIT', (first, second)
with urlopen(Request(base, headers={'Authorization': 'Bearer fictional-fixture'}), timeout=5) as response:
    bypass = response.headers.get('X-Cache')
    response.read()
assert bypass == 'BYPASS', bypass
print('PASS: product cache hit and Authorization bypass')
