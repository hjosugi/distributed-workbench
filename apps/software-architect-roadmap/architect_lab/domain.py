"""Functional core: business rules have no network or database dependency."""
from dataclasses import dataclass
from typing import Protocol

MAX_AMOUNT = 10**12


@dataclass(frozen=True)
class Line:
    sku: str
    quantity: int
    unit_price: int

    def __post_init__(self):
        if not isinstance(self.sku, str) or not self.sku or len(self.sku) > 100:
            raise ValueError("sku must contain 1..100 characters")
        if type(self.quantity) is not int or not 1 <= self.quantity <= 1000:
            raise ValueError("quantity must be an integer in 1..1000")
        if type(self.unit_price) is not int or not 0 <= self.unit_price <= MAX_AMOUNT:
            raise ValueError("unit_price must be a non-negative integer")


def total(lines: list[Line]) -> int:
    if not 1 <= len(lines) <= 100:
        raise ValueError("an order needs 1..100 lines")
    result = sum(line.quantity * line.unit_price for line in lines)
    if result > MAX_AMOUNT:
        raise ValueError("order amount exceeds the limit")
    return result


class OrderRepository(Protocol):
    def place(self, key: str, lines: list[Line], *, fail_after_insert: bool = False) -> dict: ...


def place_order(repository: OrderRepository, key: str, lines: list[Line]) -> dict:
    total(lines)
    return repository.place(key, lines)
