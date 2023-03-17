"""
# Properties

Properties are a simple key-value store for arbitrary data.
Keys must be strings. Values may be any type.

Properties serve as a handy place for storing "off-schema" data 
on HDL objects such as Signals, Modules, and Instances.
"""

from typing import Dict, Any
from dataclasses import field

from .datatype import datatype


@datatype
class Properties:
    """
    # Properties

    Properties are a simple key-value store for arbitrary data.
    Keys must be strings. Values may be any type.

    Properties serve as a handy place for storing "off-schema" data
    on HDL objects such as Signals, Modules, and Instances.
    """

    # Wrapped dictionary
    inner: Dict[str, Any] = field(default_factory=dict)

    """ 
    Primary API: `set`, `get`, `remove`, and their dict-like counterparts.
    """

    def set(self, key: str, value: Any) -> None:
        """Set property `key` to `value`.
        Raises a `TypeError` if `key` is not a string. `value` may be any type."""
        if not isinstance(key, str):
            raise TypeError(f"key must be str, not {type(key)}")
        self.inner[key] = value

    def get(self, key: str) -> Any:
        """Get property `key`.
        Raises a `TypeError` if `key` is not a string."""
        if not isinstance(key, str):
            raise TypeError(f"key must be str, not {type(key)}")
        return self.inner.get(key)

    def remove(self, key: str) -> None:
        """Remove property `key`.
        Raises a `TypeError` if `key` is not a string."""
        if not isinstance(key, str):
            raise TypeError(f"key must be str, not {type(key)}")
        del self.inner[key]

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.remove(key)

    """
    Dictionary wrapper special methods
    """

    def __repr__(self) -> str:
        return f"Properties({self.inner})"

    def __contains__(self, key: str) -> bool:
        return key in self.inner

    def __len__(self) -> int:
        return len(self.inner)

    def __iter__(self):
        return iter(self.inner)

    def __eq__(self, other) -> bool:
        return self.inner == other.inner
