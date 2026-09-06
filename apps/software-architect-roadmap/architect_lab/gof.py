"""All 23 GoF patterns, each with a small observable example."""
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
import json


def factory_method():
    class Exporter(ABC):
        @abstractmethod
        def create_encoder(self): ...
        def export(self, value):
            return self.create_encoder()(value)
    class JsonExporter(Exporter):
        def create_encoder(self):
            return json.dumps
    return JsonExporter().export({"total": 3000})


def abstract_factory():
    class JsonFamily:
        def writer(self): return json.dumps
        def reader(self): return json.loads
    class ReprFamily:
        def writer(self): return repr
        def reader(self):
            from ast import literal_eval
            return literal_eval
    def roundtrip(factory):
        return factory.reader()(factory.writer()([1, 2]))
    return [roundtrip(JsonFamily()), roundtrip(ReprFamily())]


def builder():
    class QueryBuilder:
        def __init__(self): self.conditions, self.parameters = [], []
        def minimum(self, value):
            self.conditions.append("total >= ?")
            self.parameters.append(value)
            return self
        def build(self):
            where = " WHERE " + " AND ".join(self.conditions) if self.conditions else ""
            return "SELECT * FROM orders" + where, tuple(self.parameters)
    return QueryBuilder().minimum(1000).build()


def prototype():
    template = {"items": [{"sku": "book", "quantity": 1}]}
    cloned = deepcopy(template)
    cloned["items"][0]["quantity"] = 2
    return [template["items"][0]["quantity"], cloned["items"][0]["quantity"]]


def singleton():
    class ProcessConfiguration:
        _instance = None
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    return ProcessConfiguration() is ProcessConfiguration()


def adapter():
    class LegacyCatalog:
        def cents(self): return 120000
    class YenCatalog:
        def __init__(self, legacy): self.legacy = legacy
        def price(self): return self.legacy.cents() // 100
    return YenCatalog(LegacyCatalog()).price()


def bridge():
    class JsonRenderer:
        def render(self, title, amount): return json.dumps({title: amount})
    class TextRenderer:
        def render(self, title, amount): return f"{title}: {amount}"
    class Report:
        def __init__(self, renderer): self.renderer = renderer
        def display(self): return self.renderer.render("revenue", 3000)
    return [Report(JsonRenderer()).display(), Report(TextRenderer()).display()]


def composite():
    @dataclass
    class Item:
        amount: int
        def total(self): return self.amount
    @dataclass
    class Bundle:
        children: list
        def total(self): return sum(child.total() for child in self.children)
    return Bundle([Item(1200), Bundle([Item(200), Item(200)])]).total()


def decorator():
    class Price:
        def total(self): return 1200
    class Shipping:
        def __init__(self, wrapped): self.wrapped = wrapped
        def total(self): return self.wrapped.total() + 300
    return Shipping(Price()).total()


def facade():
    class Checkout:
        def __init__(self, inventory, payment):
            self.inventory, self.payment = inventory, payment
        def buy(self, sku):
            self.inventory(sku)
            self.payment(1200)
    calls = []
    Checkout(lambda sku: calls.append("reserve:" + sku),
             lambda value: calls.append("charge:" + str(value))).buy("book")
    return calls


def flyweight():
    @dataclass(frozen=True)
    class Product:
        sku: str
    @lru_cache(maxsize=100)
    def product(sku): return Product(sku)
    lines = [(product("book"), 1), (product("book"), 3)]
    return {"shared": lines[0][0] is lines[1][0], "quantities": [x[1] for x in lines]}


def proxy():
    calls = []
    class Catalog:
        def get(self, sku):
            calls.append(sku)
            return 1200
    class CachedCatalog:
        def __init__(self, target): self.target, self.cache = target, {}
        def get(self, sku):
            if sku not in self.cache:
                self.cache[sku] = self.target.get(sku)
            return self.cache[sku]
    catalog = CachedCatalog(Catalog())
    return {"prices": [catalog.get("book"), catalog.get("book")], "origin_calls": len(calls)}


def chain_of_responsibility():
    class Check:
        def __init__(self, predicate, error, next_check=None):
            self.predicate, self.error, self.next_check = predicate, error, next_check
        def handle(self, request):
            if not self.predicate(request): return self.error
            return self.next_check.handle(request) if self.next_check else "accepted"
    chain = Check(lambda x: x["authenticated"], "401",
                  Check(lambda x: x["quantity"] > 0, "400"))
    return [chain.handle(x) for x in [{"authenticated": False, "quantity": 1},
            {"authenticated": True, "quantity": 0}, {"authenticated": True, "quantity": 1}]]


def command():
    class Add:
        def __init__(self, cart, sku): self.cart, self.sku = cart, sku
        def execute(self): self.cart.append(self.sku)
        def undo(self): self.cart.pop()
    cart = []
    action = Add(cart, "book")
    action.execute()
    before = list(cart)
    action.undo()
    return [before, cart]


def interpreter():
    class AtLeast:
        def __init__(self, limit): self.limit = limit
        def evaluate(self, total): return total >= self.limit
    class And:
        def __init__(self, left, right): self.left, self.right = left, right
        def evaluate(self, total): return self.left.evaluate(total) and self.right.evaluate(total)
    expression = And(AtLeast(1000), AtLeast(2000))
    return [expression.evaluate(1500), expression.evaluate(3000)]


def iterator():
    class Pages:
        def __init__(self, fetch): self.fetch = fetch
        def __iter__(self):
            page = 0
            while True:
                items = self.fetch(page)
                if not items: return
                yield from items
                page += 1
    data = [[1, 2], [3], []]
    return list(Pages(lambda page: data[page]))


def mediator():
    class Mediator:
        def __init__(self): self.colleagues = {}
        def register(self, name, receiver): self.colleagues[name] = receiver
        def send(self, destination, message): self.colleagues[destination](message)
    received = []
    mediator = Mediator()
    mediator.register("inventory", lambda msg: received.append("inventory:" + msg))
    mediator.register("billing", lambda msg: received.append("billing:" + msg))
    mediator.send("inventory", "reserve")
    mediator.send("billing", "charge")
    return received


def memento():
    class Editor:
        def __init__(self): self.text = "draft"
        def save(self): return self.text
        def restore(self, snapshot): self.text = snapshot
    editor = Editor()
    snapshot = editor.save()
    editor.text = "changed"
    editor.restore(snapshot)
    return editor.text


def observer():
    class Subject:
        def __init__(self): self.subscribers = []
        def subscribe(self, callback): self.subscribers.append(callback)
        def publish(self, event):
            for callback in self.subscribers: callback(event)
    output = []
    subject = Subject()
    subject.subscribe(lambda x: output.append("analytics:" + x))
    subject.subscribe(lambda x: output.append("billing:" + x))
    subject.publish("OrderPlaced")
    return output


def state():
    class Draft:
        def pay(self, order): order.state = Paid()
        def ship(self, order): raise ValueError("payment required")
    class Paid:
        def pay(self, order): raise ValueError("already paid")
        def ship(self, order): order.state = Shipped()
    class Shipped:
        def pay(self, order): raise ValueError("already paid")
        def ship(self, order): raise ValueError("already shipped")
    class Order:
        def __init__(self): self.state = Draft()
        def pay(self): self.state.pay(self)
        def ship(self): self.state.ship(self)
    order = Order()
    try: order.ship()
    except ValueError: rejected = True
    else: rejected = False
    order.pay()
    order.ship()
    return {"state": type(order.state).__name__, "early_ship_rejected": rejected}


def strategy():
    def price(amount, discount): return discount(amount)
    return [price(1000, lambda amount: amount), price(1000, lambda amount: amount * 9 // 10)]


def template_method():
    class Importer:
        def run(self, text): return sum(self.parse(text))
        def parse(self, text): raise NotImplementedError
    class CsvImporter(Importer):
        def parse(self, text): return map(int, text.split(","))
    class JsonImporter(Importer):
        def parse(self, text): return json.loads(text)
    return [CsvImporter().run("1,2,3"), JsonImporter().run("[1,2,3]")]


def visitor():
    @dataclass
    class Book:
        price: int
        def accept(self, visitor): return visitor.book(self)
    @dataclass
    class Food:
        price: int
        def accept(self, visitor): return visitor.food(self)
    class DemoTax:
        def book(self, item): return item.price // 10
        def food(self, item): return item.price * 8 // 100
    return [item.accept(DemoTax()) for item in [Book(1000), Food(1000)]]


PATTERNS = [factory_method, abstract_factory, builder, prototype, singleton, adapter,
            bridge, composite, decorator, facade, flyweight, proxy, chain_of_responsibility,
            command, interpreter, iterator, mediator, memento, observer, state, strategy,
            template_method, visitor]


def run_all():
    return {pattern.__name__: pattern() for pattern in PATTERNS}
