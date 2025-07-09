# traceattrs

A lightweight Python library to automatically track changes to object attributes over time. Designed to monitor state changes without boilerplate or intrusive instrumentation.

## Features
- Track every change to any attribute of your class instances
- Works with regular classes, dataclasses and classes with `__slots__`
- Supports inheritance: tracks attribute changes in both base and derived classes
- **Supports `copy` and `deepcopy` operations**: including all combinations and for slotted classes
- Attribute history is tracked independently for each new object created via copy or deepcopy
- Access attribute change history via dot notation
- Clear history for specific attributes or all attributes
- Pure Python, no dependencies

## Installation

Install directly from the Git repository:

```bash
pip install git+https://github.com/alenjantony/traceattrs.git
```

## Usage

Decorate your class with `@traceattrs` to enable attribute history:

```python
from traceattrs import traceattrs

@traceattrs
class SimpleClassExample:
    def __init__(self, x):
        self.x = x

obj = SimpleClassExample(10)
obj.x = 20
obj.x = 30

print(obj.history.x)  # [(None, 10), (10, 20), (20, 30)]
```

### With Dataclasses

```python
from dataclasses import dataclass
from traceattrs import traceattrs

@traceattrs
@dataclass
class DataClassExample:
    x: int = 0
    y: int = 0

obj = DataClassExample(1, 2)
obj.x = 5
print(obj.history.x)  # [(0, 1), (1, 5)]
```

### With `__slots__`

```python
from dataclasses import dataclass
from traceattrs import traceattrs

@traceattrs
@dataclass(slots=True)
class SlotsDataClassExample:
    def __init__(self, x, y):
        self.x = x
        self.y = y

obj = SlotsDataClassExample(1, 2)
obj.x = 3
print(obj.history.x)  # [(None, 1), (1, 3)]
```

### Copy and Deepcopy Support

You can safely use `copy.copy()` and `copy.deepcopy()` on any class decorated with `@traceattrs`.  
Each new object will have its own independent attribute history, including for slotted classes and any combination of copy/deepcopy operations.

```python
import copy

@traceattrs
class SimpleClassExample:
    def __init__(self, x):
        self.x = x

obj1 = SimpleClassExample(10)
obj1.x = 20

obj2 = copy.copy(obj1)
obj2.x = 99

obj3 = copy.deepcopy(obj2)
obj3.x = 123

print(obj1.history.x)  # [(None, 10), (10, 20)]
print(obj2.history.x)  # [(None, 10), (10, 20), (20, 99)]
print(obj3.history.x)  # [(None, 10), (10, 20), (20, 99), (99, 123)]
```

## Accessing and Managing History

- `obj.history.<attr>`: List of (old_value, new_value) tuples for the attribute
- `obj.history.get_all()`: Dict of all attribute histories
- `obj.history.clear('attr')`: Clear history for a specific attribute
- `obj.history.clear()`: Clear all history

## Testing

Run the test suite with pytest:

```bash
pip install pytest
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
