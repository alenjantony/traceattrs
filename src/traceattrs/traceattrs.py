"""
traceattrs: Attribute change tracking decorator for Python classes.

This module provides a class decorator, `traceattrs`, that automatically tracks all changes to instance attributes. 
It supports regular classes, dataclasses, and classes with __slots__, and exposes attribute change history via dot notation.
"""

from collections import defaultdict
from typing import Optional


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
    """Class decorator to track attribute changes on instances."""
    original_setattr = getattr(cls, '__setattr__', object.__setattr__)
    original_init = getattr(cls, '__init__', lambda self: None)

    def custom_init(self, *args, **kwargs):
        # Initialize history for this instance
        _instance_history[id(self)] = defaultdict(list)
        original_init(self, *args, **kwargs)

    def custom_setattr(self, name: str, value: any) -> None:
        """Intercepts attribute assignment to record old and new values in the instance's history."""
        obj_id = id(self)
        old_value = getattr(self, name, None)
        _instance_history[obj_id][name].append((old_value, value))
        original_setattr(self, name, value)

    def get_history(self) -> HistoryAccessor:
        """Returns a HistoryAccessor for accessing this instance's attribute change history."""
        return HistoryAccessor(_instance_history[id(self)])

    cls.__init__ = custom_init
    cls.__setattr__ = custom_setattr
    cls.history = property(get_history)
    return cls
