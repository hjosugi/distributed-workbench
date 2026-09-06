"""Verify a real Redis hash and expiration; delete only this test's key."""
import subprocess
import uuid

key = 'architect:test:' + uuid.uuid4().hex

def redis(*args):
    return subprocess.run(['docker', 'compose', 'exec', '-T', 'redis', 'redis-cli', '--raw', *args],
                          text=True, capture_output=True, check=True, timeout=10).stdout.strip()

try:
    assert redis('HSET', key, 'price', '1200') == '1'
    assert redis('HGET', key, 'price') == '1200'
    assert redis('EXPIRE', key, '60') == '1'
    assert 0 < int(redis('TTL', key)) <= 60
    print('PASS: Redis hash roundtrip and expiration')
finally:
    redis('DEL', key)
