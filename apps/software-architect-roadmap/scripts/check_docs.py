"""Validate inventory and local Markdown links without making network requests."""
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / 'roadmap.json').read_text())
assert len(rows) == 53 and len({x['id'] for x in rows}) == 53, '53 unique topics required'
assert [x['number'] for x in rows] == list(range(1, 54)), 'topic numbers must be contiguous'
assert list(Counter(x['group'] for x in rows).values()) == [4, 5, 8, 6, 8, 8, 8, 6], 'category mismatch'
for row in rows:
    for relative in [row['document'], *row['implementation']]:
        assert (ROOT / relative).is_file(), f'Missing mapped file: {relative}'
for path in ROOT.rglob('*.md'):
    if any(part in {'.venv', 'node_modules'} for part in path.parts): continue
    text = path.read_text()
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        if target.startswith(('http:', 'https:', '#', 'mailto:')): continue
        target = target.split('#')[0]
        assert (path.parent / target).exists(), f'Broken link: {path.relative_to(ROOT)} -> {target}'
print('PASS: 53 topics, 8 groups, mapped implementation files, and local Markdown links')
