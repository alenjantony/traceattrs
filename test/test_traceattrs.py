"""
Unit tests for the traceattrs attribute tracking library.
Covers regular classes, dataclasses, slotted classes, inheritance, and history management.
"""

import pytest
import copy
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


def test_copy_history():
    """Test that copying objects preserves independent history tracking."""
    obj1 = RegularClass(5, 6)
    obj1.x = 50
    obj1.y = 60
    obj2 = copy.copy(obj1)
    # Mutate copy
    obj2.x = 500
    # Original should not be affected by changes to copy
    assert obj1.history.x == [(None, 5), (5, 50)], "Original x history after copy"
    assert obj1.history.y == [(None, 6), (6, 60)], "Original y history after copy"
    # Copy should have its own independent history
    assert obj2.history.x == [(None, 5), (5, 50), (50, 500)], "Shallow copy x history"
    assert obj2.history.y == [(None, 6), (6, 60)], "Shallow copy y history"


def test_deepcopy_history():
    """Test that deep copying objects preserves independent history tracking."""
    obj1 = RegularClass(5, 6)
    obj1.x = 50
    obj1.y = 60
    obj2 = copy.deepcopy(obj1)
    # Mutate deep copy
    obj2.y = 600
    # Original should not be affected by changes to deep copy
    assert obj1.history.x == [(None, 5), (5, 50)], "Original x history after deepcopy"
    assert obj1.history.y == [(None, 6), (6, 60)], "Original y history after deepcopy"
    # Deep copy should have its own independent history
    assert obj2.history.x == [(None, 5), (5, 50)], "Deep copy x history"
    assert obj2.history.y == [(None, 6), (6, 60), (60, 600)], "Deep copy y history"


def test_copy_after_copy():
    """Test that copying an object after another copy preserves independent history tracking."""
    obj1 = RegularClass(1, 2)
    obj1.x = 10
    obj2 = copy.copy(obj1)
    obj3 = copy.copy(obj2)
    obj3.x = 99
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after two copies"
    assert obj2.history.x == [(None, 1), (1, 10)], "First copy x history after two copies"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 99)], "Second copy x history after two copies"


def test_deepcopy_after_deepcopy():
    """Test that deep copying an object after another deepcopy preserves independent history tracking."""
    obj1 = RegularClass(1, 2)
    obj1.x = 10
    obj2 = copy.deepcopy(obj1)
    obj3 = copy.deepcopy(obj2)
    obj3.x = 77
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after two deepcopies"
    assert obj2.history.x == [(None, 1), (1, 10)], "First deepcopy x history after two deepcopies"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 77)], "Second deepcopy x history after two deepcopies"


def test_copy_after_deepcopy():
    """Test that copying an object after a deepcopy preserves independent history tracking."""
    obj1 = RegularClass(1, 2)
    obj1.x = 10
    obj2 = copy.deepcopy(obj1)
    obj3 = copy.copy(obj2)
    obj3.x = 55
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after deepcopy then copy"
    assert obj2.history.x == [(None, 1), (1, 10)], "Deepcopy x history after deepcopy then copy"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 55)], "Copy x history after deepcopy then copy"


def test_deepcopy_after_copy():
    """Test that deep copying an object after a copy preserves independent history tracking."""
    obj1 = RegularClass(1, 2)
    obj1.x = 10
    obj2 = copy.copy(obj1)
    obj3 = copy.deepcopy(obj2)
    obj3.x = 42
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after copy then deepcopy"
    assert obj2.history.x == [(None, 1), (1, 10)], "Copy x history after copy then deepcopy"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 42)], "Deepcopy x history after copy then deepcopy"


def test_copy_history_slotted():
    """Test copying a slotted dataclass preserves independent history tracking."""
    obj1 = SlottedDataClass(1, 2)
    obj1.x = 10
    obj2 = copy.copy(obj1)
    obj2.x = 20
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after copy (slotted)"
    assert obj2.history.x == [(None, 1), (1, 10), (10, 20)], "Copy x history after copy (slotted)"


def test_deepcopy_history_slotted():
    """Test deep copying a slotted dataclass preserves independent history tracking."""
    obj1 = SlottedDataClass(1, 2)
    obj1.x = 10
    obj2 = copy.deepcopy(obj1)
    obj2.x = 20
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after deepcopy (slotted)"
    assert obj2.history.x == [(None, 1), (1, 10), (10, 20)], "Deepcopy x history after deepcopy (slotted)"


def test_copy_after_copy_slotted():
    """Test copying a slotted dataclass after another copy preserves independent history tracking."""
    obj1 = SlottedDataClass(1, 2)
    obj1.x = 10
    obj2 = copy.copy(obj1)
    obj3 = copy.copy(obj2)
    obj3.x = 99
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after two copies (slotted)"
    assert obj2.history.x == [(None, 1), (1, 10)], "First copy x history after two copies (slotted)"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 99)], "Second copy x history after two copies (slotted)"


def test_deepcopy_after_deepcopy_slotted():
    """Test deep copying a slotted dataclass after another deepcopy preserves independent history tracking."""
    obj1 = SlottedDataClass(1, 2)
    obj1.x = 10
    obj2 = copy.deepcopy(obj1)
    obj3 = copy.deepcopy(obj2)
    obj3.x = 77
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after two deepcopies (slotted)"
    assert obj2.history.x == [(None, 1), (1, 10)], "First deepcopy x history after two deepcopies (slotted)"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 77)], "Second deepcopy x history after two deepcopies (slotted)"


def test_copy_after_deepcopy_slotted():
    """Test copying a slotted dataclass after a deepcopy preserves independent history tracking."""
    obj1 = SlottedDataClass(1, 2)
    obj1.x = 10
    obj2 = copy.deepcopy(obj1)
    obj3 = copy.copy(obj2)
    obj3.x = 55
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after deepcopy then copy (slotted)"
    assert obj2.history.x == [(None, 1), (1, 10)], "Deepcopy x history after deepcopy then copy (slotted)"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 55)], "Copy x history after deepcopy then copy (slotted)"


def test_deepcopy_after_copy_slotted():
    """Test deep copying a slotted dataclass after a copy preserves independent history tracking."""
    obj1 = SlottedDataClass(1, 2)
    obj1.x = 10
    obj2 = copy.copy(obj1)
    obj3 = copy.deepcopy(obj2)
    obj3.x = 42
    assert obj1.history.x == [(None, 1), (1, 10)], "Original x history after copy then deepcopy (slotted)"
    assert obj2.history.x == [(None, 1), (1, 10)], "Copy x history after copy then deepcopy (slotted)"
    assert obj3.history.x == [(None, 1), (1, 10), (10, 42)], "Deepcopy x history after copy then deepcopy (slotted)"


def test_multiple_copies():
    """Test multiple sequential copies preserve correct and independent history tracking."""
    obj1 = RegularClass(10, 0)
    obj1.x = 20

    obj2 = copy.copy(obj1)
    obj2.x = 99

    obj3 = copy.copy(obj2)
    obj3.x = 123

    assert obj1.history.x == [(None, 10), (10, 20)], "Original x history after copy-deepcopy chain"
    assert obj2.history.x == [(None, 10), (10, 20), (20, 99)], "Copy x history after copy-deepcopy chain"
    assert obj3.history.x == [(None, 10), (10, 20), (20, 99), (99, 123)], "Deepcopy x history after copy"
