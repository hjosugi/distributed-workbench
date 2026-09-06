# TDD walkthrough: a bulk-order discount

The committed implementation already passes its tests. This exercise demonstrates a red/green/refactor cycle on a **new rule**, rather than claiming a development history from passing tests.

Requirement: a subtotal of at least 5000 yen receives a 10% discount. Smaller totals do not. The result is integer yen, rounded down. Negative input is invalid. Work on an exercise branch or a disposable copy.

## Red

Add `tests/test_discount.py`:

```python
import unittest
from architect_lab.domain import discounted_total

class DiscountTests(unittest.TestCase):
    def test_threshold_and_rounding(self):
        self.assertEqual(discounted_total(4999), 4999)
        self.assertEqual(discounted_total(5000), 4500)
        self.assertEqual(discounted_total(5001), 4500)

    def test_negative_input(self):
        with self.assertRaises(ValueError):
            discounted_total(-1)
```

Run `python3 -m unittest discover -s tests -p test_discount.py -v`. It fails because the operation does not exist yet. This is an intended exercise failure and is not in the default suite.

## Green

Add the completed behavior to `domain.py`:

```python
def discounted_total(subtotal: int) -> int:
    if type(subtotal) is not int or subtotal < 0:
        raise ValueError("subtotal must be a non-negative integer")
    return subtotal * 9 // 10 if subtotal >= 5000 else subtotal
```

The test should now pass. Add cases for zero, bool, float, and a large amount if those inputs matter at the public boundary.

## Refactor

Move a configurable discount into a Strategy only when there is a second actual policy. Keep the test focused on returned amounts, not helper calls. Do not connect the discount to accepted-order replay until the business rule says whether an accepted order keeps the original discount.

Run the full suite after the change. Explain: **I write a failing behavior test, implement the rule, and refactor while preserving behavior.**
