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

from typing import TypeVar, Type, Any

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


def no_setattr(cls: Type[T]) -> Type[T]:
    """
    Decorator to "freeze" an object's attributes after construction.
    This is not called "frozen" or similar (unlike the std-lib),
    because it is much more difficult to actually freeze a Python object's inner fields.
    So, `no_setattr` types *are not* immutable - their attributes can still be changed,
    but *new attributes* cannot be added.
    """

    if "__setattr__" in cls.__dict__:
        msg = f"Internal Error: `__setattr__` doubly defined for {cls}"
        raise RuntimeError(msg)

    def __setattr__(self, key: str, val: Any) -> None:
        """Only allow setting special attributes after initialization."""

        special: bool = key.startswith("_")  # Special variables are always allowed
        inited: bool = object.__getattribute__(self, "_initialized")

        if special or not inited:
            return object.__setattr__(self, key, val)

        # FIXME: maybe allow customizing the error handler?
        msg = f"Cannot set attributes on {self} - attempting {key} = {val}"
        raise RuntimeError(msg)

    cls.__setattr__ = __setattr__
    return cls


def only_set_known_attrs(cls: Type[T]) -> Type[T]:
    """
    Decorator for "only allow setting existing attributes".
    Allows setting attributes only under three conditions:
    * The attribute name starts with an underscore, e.g. `__init__`, or
    * The object is still in its "bootstrapping phase", i.e. `_initialized` is `False`, or
    * The attribute already exists on the object
    """

    if "__setattr__" in cls.__dict__:
        msg = f"Internal Error: `__setattr__` doubly defined for {cls}"
        raise RuntimeError(msg)

    def __setattr__(self, key: str, val: Any) -> None:
        """Only allow setting existing attributes."""

        special: bool = key.startswith("_")  # Special variables are always allowed
        inited: bool = object.__getattribute__(self, "_initialized")

        if special or not inited:
            return object.__setattr__(self, key, val)

        # Check if the attribute already exists
        # This generally wants to "reach around" any of our other `__getattr__` magic.
        # If it doesn't exist, we'll get an exception, which we'll catch and re-raise.
        try:
            object.__getattribute__(self, key)
        except:
            # FIXME: maybe allow customizing the error handler?
            msg = f"Cannot set attributes on {self} - attempting {key} = {val}"
            raise RuntimeError(msg)
        else:
            return object.__setattr__(self, key, val)

    cls.__setattr__ = __setattr__
    return cls
