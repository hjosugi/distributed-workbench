"""Parse YAML/JSON config files without contacting any external service."""
from pathlib import Path
import json
import sys
try:
    import yaml
except ImportError:
    raise SystemExit('Install requirements-dev.txt to validate YAML.')
ROOT = Path(__file__).resolve().parents[1]
files = [ROOT / 'compose.yaml', *sorted((ROOT / 'infra').rglob('*.yaml'))]
for path in files:
    documents = list(yaml.safe_load_all(path.read_text()))
    if not documents or any(not isinstance(x, dict) for x in documents):
        raise SystemExit(f'Invalid YAML document: {path}')
for path in (ROOT / 'data').glob('*.json'):
    json.loads(path.read_text())
print(f'PASS: {len(files)} YAML files and JSON fixtures parsed. This is not a service runtime test.')
