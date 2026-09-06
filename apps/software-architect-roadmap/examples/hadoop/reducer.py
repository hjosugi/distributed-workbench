"""Hadoop Streaming reducer: sorted SKU/tab/quantity -> totals."""
import sys
current, total = None, 0
for line in sys.stdin:
    sku, quantity = line.rstrip('\n').split('\t')
    if current is not None and sku != current:
        print(f'{current}\t{total}')
        total = 0
    current = sku
    total += int(quantity)
if current is not None:
    print(f'{current}\t{total}')
