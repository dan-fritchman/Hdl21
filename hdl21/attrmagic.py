"""
# Hdl21 Attribute Magic 

Facilities for all of the `getattr` and `setattr` "magic" used by Hdl21 types. 

There is fairly little "magic" (ahem) being performed here; 
this module serves as more of a written reminder of how Hdl21's `getattr` and `setattr` overrides work. 

Getting them completely straight can be a pain, including a few complications: 
* During object initialization, and for setting "built-ins" e.g. the "dunder" methods 
* Many failures tend to occur only while *debugging*, e.g. with `pdb` or an IDE plugin. 
  * This makes tracking down problems with this scheme aways more difficult, as unit-tests fail to catch them. 

The scheme adopted here is what we've empirically observed to be the most reliable. 
* A `_initialized` boolean field is set to `False` as the VERY FIRST thing in object construction.
* All "magic methods" check the value of this field, and run "regular" `setattr` and `getattr` if it is `False`.
* The `_initialized` field is then set to `True` at the end of object construction.

The methods here primarily serve as a central reminder of and reusable source for this scheme. 
"""

from typing import TypeVar, Type


T = TypeVar("T")


def init(cls: Type[T]) -> Type[T]:
    """
    Initialization decorator for "attr magic" types.

    Sets an `_initialized` field to `False` as part of a `__new__` method, so that `__init__` need not remember to do so.
    Constructors are required to set `_initialized` to `True` when *all* construction has completed.
    For inherited types, this generally includes both parent and subclass initialization.

    NOTE: this is a very important part of the `setattr` and `getattr` methods,
    particularly for their "bootstrapping phase" during object creation.
    """

    if "__new__" in cls.__dict__:
        msg = f"Internal Error: `__new__` doubly defined for {cls}"
        raise RuntimeError(msg)

    def __new__(cls, *_, **__):
        inst = object.__new__(cls)
        object.__setattr__(inst, "_initialized", False)
        return inst

    cls.__new__ = __new__
    return cls
