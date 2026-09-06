"""Start each requested runtime and verify the common HTTP contract."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {
    'python': [sys.executable, 'examples/catalog/python/catalog.py'],
    'javascript': ['node', 'examples/catalog/javascript/catalog.mjs'],
    'java': ['java', 'examples/catalog/java/Catalog.java'],
    'go': ['go', 'run', 'examples/catalog/go/main.go'],
}
parser = argparse.ArgumentParser()
parser.add_argument('languages', nargs='*', choices=list(COMMANDS), default=[])
args = parser.parse_args()
for language in args.languages or list(COMMANDS):
    command = COMMANDS[language]
    if not shutil.which(command[0]):
        raise SystemExit(f'Missing runtime: {command[0]}')
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    environment = {**os.environ, 'PORT': str(port), 'BIND_HOST': '127.0.0.1', 'GOWORK': 'off'}
    with open(os.devnull, 'w') as output:
        process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=output, stderr=subprocess.PIPE, text=True, start_new_session=os.name != "nt")
        try:
            base = f'http://127.0.0.1:{port}'
            deadline = time.monotonic() + 40
            while True:
                if process.poll() is not None:
                    raise RuntimeError(process.stderr.read())
                try:
                    with urlopen(base + '/health', timeout=1) as response:
                        assert json.load(response) == {'status': 'ok'}
                    break
                except (URLError, TimeoutError):
                    if time.monotonic() >= deadline: raise
                    time.sleep(0.1)
            with urlopen(base + '/products', timeout=3) as response:
                assert json.load(response) == [{'sku': 'book', 'unit_price': 1200}, {'sku': 'pen', 'unit_price': 200}]
            for path, method, status in [('/missing', 'GET', 404), ('/products', 'POST', 405)]:
                try:
                    with urlopen(Request(base + path, method=method), timeout=3) as response:
                        actual = response.status
                except HTTPError as error:
                    actual = error.code
                    error.close()
                assert actual == status, (language, actual, status)
            print(f'PASS: {language} catalog contract')
        finally:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            try: process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                if os.name != "nt":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.communicate(timeout=5)
