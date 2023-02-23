""" 
# Datatypes Decorator 

Wraps `@pydantic.dataclasses.dataclass` so that we can make forward type-references 
throughout the package, and then sort them all out at the end of import-time. 

The intended usage is such that `__init__.py` includes

```python
# Import all the other code 
from .other_module1 import Whatever
from .other_module2 import WhateverElse

# Then at the end, get and run the forward-reference updater-method
from .datatype import _update_forward_refs

_update_forward_refs()
```

Notes: 
* `@datatype` is designed solely to work *intra-package*. 
  * Attempts to import and use it after `__init__.py` completes will generally fail. 
  * Importing this function into other packages is therefore highly discouraged. (Copying it is quite easy though.) 
* `@datatype` only works on modules which are imported before `_update_forward_refs()` is run. 
  * Generally this means modules which are imported as part of `__init__.py`
* `@datatype` is designed solely to work on `pydantic.dataclasses.dataclass`es. 
  * Notable exceptions include *union types* thereof, which do not have the necessary fields/ methods. 
"""

from pydantic.dataclasses import dataclass
from typing import TypeVar, Type

# The list of defined datatypes
datatypes = []

T = TypeVar("T")


def datatype(cls: Type[T]) -> Type[T]:
    """Register a class as a datatype."""

    # Convert `cls` to a `pydantic.dataclasses.dataclass`,
    # and add it to the list of datatypes
    cls = dataclass(cls)
    datatypes.append(cls)
    return cls


def _update_forward_refs():
    """Update all the forward type-references"""
    for tp in datatypes:
        tp.__pydantic_model__.update_forward_refs()
