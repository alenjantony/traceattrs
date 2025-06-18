"""
Unit tests for the traceattrs attribute tracking library.
Covers regular classes, dataclasses, slotted classes, inheritance, and history management.
"""

import pytest
from dataclasses import dataclass

from traceattrs import traceattrs


@traceattrs
class RegularClass:
    """A regular class for attribute tracking tests."""
    def __init__(self, x, y):
        self.x = x
        self.y = y


@traceattrs
@dataclass
class DataClassExample:
    """A dataclass for attribute tracking tests."""
    x: int = 0
    y: int = 0


@traceattrs
@dataclass(slots=True)
class SlottedDataClass:
    """A slotted dataclass for attribute tracking tests."""
    x: int = 0
    y: int = 0


@traceattrs
class ManualSlots:
    """A class with manually defined __slots__ for attribute tracking tests."""
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Base:
    """Base class with __slots__ for inheritance tests."""
    __slots__ = ['a']
    def __init__(self, a):
        self.a = a


@traceattrs
class Derived(Base):
    """Derived class with __slots__ for inheritance tests."""
    __slots__ = ['b']
    def __init__(self, a, b):
        super().__init__(a)
        self.b = b


def assign_common_attrs(obj):
    """Assign a set of common attributes to an object for testing history tracking."""
    obj.x = 50
    obj.x = 200
    obj.z = 50
    obj.z = 200
    obj._prot = 50
    obj._prot = 200
    obj.__priv = 50
    obj.__priv = 200
    obj.val = 50
    obj.val = 50
    obj.s = "Hello"
    obj.s = "HelloWorld"


def test_regular_class():
    """Test attribute tracking for a regular class."""
    obj = RegularClass(1, 2)
    assign_common_attrs(obj)
    assert obj.history.x == [(None, 1), (1, 50), (50, 200)], "Regular attribute 'x' tracking"
    assert obj.history.z == [(None, 50), (50, 200)], "Dynamic attribute 'z' tracking"
    assert obj.history._prot == [(None, 50), (50, 200)], "Protected attribute '_prot' tracking"
    assert obj.history.__priv == [(None, 50), (50, 200)], "Private attribute '__priv' tracking"
    assert obj.history.val == [(None, 50), (50, 50)], "Same value attribute 'val' tracking"
    assert obj.history.s == [(None, "Hello"), ("Hello", "HelloWorld")], "Non integer attribute 's' tracking"


def test_dataclass_tracking():
    """Test attribute tracking for a dataclass and its default values."""
    obj = DataClassExample(1, 2)
    obj_default_value = DataClassExample()
    obj_default_value.x = 50
    assign_common_attrs(obj)
    assert obj.history.x == [(0, 1), (1, 50), (50, 200)], "Regular attribute 'x' tracking"
    assert obj.history.z == [(None, 50), (50, 200)], "Dynamic attribute 'z' tracking"
    assert obj.history._prot == [(None, 50), (50, 200)], "Protected attribute '_prot' tracking"
    assert obj.history.__priv == [(None, 50), (50, 200)], "Private attribute '__priv' tracking"
    assert obj.history.val == [(None, 50), (50, 50)], "Same value attribute 'val' tracking"
    assert obj.history.s == [(None, "Hello"), ("Hello", "HelloWorld")], "Non integer attribute 's' tracking"
    assert obj_default_value.history.x == [(0, 0), (0, 50)], "Regular attribute 'x' with default value tracking"


def test_slotted_dataclass():
    """Test attribute tracking for a slotted dataclass."""
    obj = SlottedDataClass(1, 2)
    obj_default_value = SlottedDataClass()
    obj_default_value.x = 50
    obj.x = 50
    obj.x = 200
    with pytest.raises(AttributeError):
        obj.z = 50
    assert obj.history.x == [(None, 1), (1, 50), (50, 200)], "Regular attribute 'x' tracking"
    assert obj_default_value.history.x == [(None, 0), (0, 50)], "Regular attribute 'x' with default value tracking"


def test_manual_slots():
    """Test attribute tracking for a class with manual __slots__."""
    obj = ManualSlots(1, 2)
    obj.x = 50
    obj.x = 200
    with pytest.raises(AttributeError):
        obj.z = 50
    assert obj.history.x == [(None, 1), (1, 50), (50, 200)], "Regular attribute 'x' tracking"


def test_inherited_slots():
    """Test attribute tracking for inherited __slots__ attributes."""
    obj = Derived(1, 2)
    obj.a = 10
    obj.b = 20
    assert obj.history.a == [(None, 1), (1, 10)], "Base class attribute 'a' tracking"
    assert obj.history.b == [(None, 2), (2, 20)], "Derived class attribute 'b' tracking"


def test_history():
    """Test get_all and clear methods for per-object history management."""
    obj1 = RegularClass(1, 1)
    obj2 = RegularClass(2, 2)
    obj1.x = 50
    obj1.y = 200
    obj2.x = 100
    obj2.y = 300
    assert obj1.history.get_all() == {
        'x': [(None, 1), (1, 50)],
        'y': [(None, 1), (1, 200)]
    }, "get_all() returns correct history dict"
    assert obj2.history.get_all() == {
        'x': [(None, 2), (2, 100)],
        'y': [(None, 2), (2, 300)]
    }, "get_all() returns correct history dict for second object"
    obj1.history.clear('x')
    assert obj1.history.get_all() == {
        'x': [],
        'y': [(None, 1), (1, 200)]
    }, "clear('x') clears only x history"
    assert obj2.history.get_all() == {
        'x': [(None, 2), (2, 100)],
        'y': [(None, 2), (2, 300)]
    }, "clear('x') on obj1 does not affect obj2"
    obj1.history.clear()
    assert obj1.history.get_all() == {}, "clear() clears all history"
    assert obj2.history.get_all() == {
        'x': [(None, 2), (2, 100)],
        'y': [(None, 2), (2, 300)]
    }, "clear() on obj1 does not affect obj2"


def test_sequential_object_history():
    """Ensure that two objects created one after another track their history independently and correctly."""
    obj1 = RegularClass(10, 20)
    obj2 = RegularClass(30, 40)
    obj1.x = 100
    obj2.x = 200
    obj1.y = 300
    obj2.y = 400
    assert obj1.history.x == [(None, 10), (10, 100)], "obj1 x history tracked correctly"
    assert obj2.history.x == [(None, 30), (30, 200)], "obj2 x history tracked correctly"
    assert obj1.history.y == [(None, 20), (20, 300)], "obj1 y history tracked correctly"
    assert obj2.history.y == [(None, 40), (40, 400)], "obj2 y history tracked correctly"
