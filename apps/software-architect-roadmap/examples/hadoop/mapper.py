"""Hadoop Streaming mapper: JSON Lines -> SKU/tab/quantity."""
import json
import sys
for line in sys.stdin:
    if not line.strip(): continue
    event = json.loads(line)
    sku, quantity = event['sku'], event['quantity']
    if not isinstance(sku, str) or not sku or any(c in sku for c in '\t\r\n'):
        raise ValueError('invalid sku')
    if type(quantity) is not int or quantity < 0:
        raise ValueError('invalid quantity')
    print(f'{sku}\t{quantity}')
