"""
# Hdl21 Connectable Decorator & Type Union

Applied to types that are "used as connections", e.g. Signal. 
"""

# Std-Lib Imports
from typing import Any, Union, TypeVar, Type

T = TypeVar("T")


def connectable(cls: Type[T]) -> Type[T]:
    """Decorator for connectable types"""
    cls.__connectable__ = True
    return cls


def is_connectable(obj: Any) -> bool:
    """Boolean indication of connect-ability"""
    return getattr(obj, "__connectable__", False)


# Union of types using `connectable`
# For checking, `is_connectable` is preferable, but this serves as a handy shorthand for many type annotations.
Connectable = Union[
    "Signal",
    "Slice",
    "Concat",
    "NoConn",
    "PortRef",
    "BundleInstance",
    "AnonymousBundle",
    "BundleRef",
]
