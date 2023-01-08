"""
# Concatenation-ability Decorator 

Solely a marker used by `Concat` for validity checking. 
"""

# Local imports
from .connect import is_connectable
from typing import TypeVar, Type

T = TypeVar("T")


def concatable(cls: Type[T]) -> Type[T]:
    """Decorator for `Concat`-compatible types."""
    if not is_connectable(cls):
        raise TypeError(f"{cls} is not connectable")
    # Just adds a "marker trait" to the class
    cls.__concatable__ = True
    return cls


def is_concatable(obj: object) -> type:
    return getattr(obj, "__concatable__", False)
