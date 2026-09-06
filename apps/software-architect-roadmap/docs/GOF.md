# All 23 GoF Patterns

Run `python3 -m architect_lab gof`. Each name below maps to a function in [gof.py](../architect_lab/gof.py). All examples are checked in [test_core.py](../tests/test_core.py).

## Creational patterns

| Pattern / function | Implementation and useful situation | Common mistake |
|---|---|---|
| Factory Method / `factory_method` | Exporter workflow calls a construction hook overridden by JsonExporter | Calling every object-creation helper a Factory Method |
| Abstract Factory / `abstract_factory` | JSON and repr families supply matching reader/writer pairs | Mixing incompatible family members |
| Builder / `builder` | Accumulate query conditions and bound parameters before creating a query | Concatenating untrusted SQL values |
| Prototype / `prototype` | Deep-copy a nested template and vary the copy | Sharing nested mutable state through a shallow copy |
| Singleton / `singleton` | Reuse one process-local configuration instance | Assuming uniqueness across threads or a cluster |

The Singleton example is single-threaded. Dependency injection is often easier to test.

## Structural patterns

| Pattern / function | Implementation and useful situation | Common mistake |
|---|---|---|
| Adapter / `adapter` | Convert a legacy minor-unit price interface into the expected interface | Silently changing units or losing precision |
| Bridge / `bridge` | Report abstraction accepts independent JSON/text renderers | Confusing planned variation with adapting an existing API |
| Composite / `composite` | Items and nested bundles share `total()` | Creating cycles in an intended tree |
| Decorator / `decorator` | Shipping wraps a price and adds behavior through the same interface | Ignoring decorator order |
| Facade / `facade` | Checkout presents one operation over inventory/payment calls | Assuming the facade makes remote effects atomic |
| Flyweight / `flyweight` | Share immutable product data, keep line quantities separate | Sharing mutable per-request state |
| Proxy / `proxy` | Cached catalog controls access and invokes the origin once | Forgetting cache invalidation and identity |

Adapter changes an interface. Decorator adds behavior. Proxy controls access. Bridge separates independently changing dimensions. Similar wrappers can have different intent.

## Behavioral patterns

| Pattern / function | Implementation and useful situation | Common mistake |
|---|---|---|
| Chain of Responsibility / `chain_of_responsibility` | Ordered auth/quantity checks reject or forward a request | Hiding which handler rejected it |
| Command / `command` | Represent cart addition with execute and undo | Assuming remote effects can always be undone |
| Interpreter / `interpreter` | Compose and evaluate a tiny threshold expression tree | Building a full language for a simple predicate |
| Iterator / `iterator` | Fetch pages while exposing one sequence of items | Ignoring errors and cancellation between pages |
| Mediator / `mediator` | Route messages to registered inventory/billing colleagues | Moving all business logic into one coordinator |
| Memento / `memento` | Save and restore editor text | Treating a local snapshot as distributed rollback |
| Observer / `observer` | Notify analytics and billing callbacks | Assuming callbacks are durable broker delivery |
| State / `state` | Draft, Paid, Shipped objects own operations and transitions | Bypassing lifecycle invariants |
| Strategy / `strategy` | Inject a discount function | Adding a class hierarchy where a function suffices |
| Template Method / `template_method` | Base import workflow parses then sums; subclasses vary parsing | Exposing too many fragile override hooks |
| Visitor / `visitor` | Book/Food dispatch to type-specific tax operations | Adding an element type without updating visitors |

Tax values are arbitrary demo values. Command undo assumes the action is the latest local change. The facade has no saga, and the proxy cache has no TTL. These are visible educational boundaries.

## Short phrases to remember

- Factory Method varies creation through a subclass.
- Abstract Factory creates a matching family.
- Strategy changes an algorithm; State changes behavior with a lifecycle.
- Template Method fixes the workflow and varies selected steps.
- Observer notifies subscribers; Mediator coordinates colleagues.
- Memento restores state; Command stores an operation.
- Visitor adds operations across stable element types.

Choose a pattern after identifying a source of change. A discount Strategy can be a function. A Repository Adapter can replace SQLite without changing validation. Do not add all 23 patterns to one application.

The names and categories follow the [GoF book from its publisher](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780321700698). All examples here are original.
