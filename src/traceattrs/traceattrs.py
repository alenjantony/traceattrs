"""
traceattrs: Attribute change tracking decorator for Python classes.

This module provides a class decorator, `traceattrs`, that automatically tracks all changes to instance attributes. 
It supports regular classes, dataclasses, and classes with __slots__, and exposes attribute change history via dot notation.
"""

from collections import defaultdict
from typing import Optional
import copy


# Maps instance id to attribute history
_instance_history: dict[int, dict[str, list[tuple[any, any]]]] = {}


class HistoryAccessor:
    """Provides dot notation access to attribute history for an object."""
    def __init__(self, history_data: dict[str, list[tuple[any, any]]]):
        self._history_data = history_data

    def __getattr__(self, name: str) -> list[tuple[any, any]]:
        return self._history_data.get(name, [])

    def __repr__(self) -> str:
        return f"HistoryAccessor({dict(self._history_data)})"

    def get_all(self) -> dict[str, list[tuple[any, any]]]:
        """Return a copy of all attribute histories."""
        return dict(self._history_data)

    def clear(self, attribute: Optional[str] = None) -> None:
        """Clear history for a specific attribute or all attributes."""
        if attribute:
            self._history_data[attribute].clear()
        else:
            self._history_data.clear()


def traceattrs(cls: type) -> type:
    """Decorator to track attribute changes on class instances."""
    original_setattr = getattr(cls, '__setattr__', object.__setattr__)
    original_init = getattr(cls, '__init__', lambda self: None)

    def custom_init(self, *args, **kwargs):
        """Initialize instance history."""
        _instance_history[id(self)] = defaultdict(list)
        original_init(self, *args, **kwargs)

    def custom_setattr(self, name: str, value: any) -> None:
        """Record attribute changes."""
        history = _instance_history.setdefault(id(self), defaultdict(list))
        history[name].append((getattr(self, name, None), value))
        original_setattr(self, name, value)

    def custom_copy(self):
        """Support copy.copy with history and slots."""
        cls = self.__class__
        result = cls.__new__(cls)
        if hasattr(self, '__dict__'):
            result.__dict__.update(self.__dict__)
        slots = getattr(self, '__slots__', ())
        for slot in slots:
            if hasattr(self, slot):
                setattr(result, slot, getattr(self, slot))
        original_history = _instance_history.get(id(self), defaultdict(list))
        _instance_history[id(result)] = copy.deepcopy(original_history)
        return result

    def custom_deepcopy(self, memo):
        """Support copy.deepcopy with history and slots."""
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        if hasattr(self, '__dict__'):
            for k, v in self.__dict__.items():
                setattr(result, copy.deepcopy(k, memo), copy.deepcopy(v, memo))
        slots = getattr(self, '__slots__', ())
        for slot in slots:
            if hasattr(self, slot):
                setattr(result, slot, copy.deepcopy(getattr(self, slot), memo))
        original_history = _instance_history.get(id(self), defaultdict(list))
        _instance_history[id(result)] = copy.deepcopy(original_history, memo)
        return result
    
    def get_history(self) -> HistoryAccessor:
        """Return history accessor for this instance."""
        return HistoryAccessor(_instance_history[id(self)])

    cls.__init__ = custom_init
    cls.__setattr__ = custom_setattr
    cls.__copy__ = custom_copy
    cls.__deepcopy__ = custom_deepcopy
    cls.history = property(get_history)
    return cls
