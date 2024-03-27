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
- `@datatype` is designed solely to work *intra-package*. 
  - Attempts to import and use it after `__init__.py` completes will generally fail. 
  - Importing this function into other packages is therefore highly discouraged. (Copying it is quite easy though.) 
- `@datatype` only works on modules which are imported before `_update_forward_refs()` is run. 
  - Generally this means modules which are imported as part of `__init__.py`
- `@datatype` is designed solely to work on `pydantic.dataclasses.dataclass`es. 
  - Notable exceptions include *union types* thereof, which do not have the necessary fields/ methods. 
"""

from typing import TypeVar, Type, Optional
from pydantic import __version__ as _pydantic_version


_pydantic_major_version = int(_pydantic_version.split(".")[0])
if _pydantic_major_version > 2 or _pydantic_major_version < 1:
    msg = "Error reading Pydantic version. Should be either 1.x or 2.x."
    raise ImportError(msg)

if _pydantic_major_version == 1:
    from pydantic import Extra, BaseModel
    from pydantic.json import pydantic_encoder as pydantic_json_encoder

    PYDANTIC_V2 = False

    class OurBaseConfig:
        allow_extra = Extra.forbid

    class AllowArbConfig(OurBaseConfig):
        arbitrary_types_allowed = True

    def _update_forward_refs():
        """Update all the forward type-references"""
        for tp in datatypes:
            tp.__pydantic_model__.update_forward_refs()

else:  # _pydantic_major_version==2
    from pydantic import Extra, BaseModel, RootModel, BeforeValidator
    from pydantic.deprecated.json import pydantic_encoder as pydantic_json_encoder

    PYDANTIC_V2 = True
    OurBaseConfig = dict(allow_extra="forbid", validate_default=True)
    AllowArbConfig = dict(
        allow_extra="forbid", validate_default=True, arbitrary_types_allowed=True
    )

    def _update_forward_refs():
        """Update all the forward type-references"""
        ...
        # for tp in datatypes:
        #     tp.model_rebuild()


from pydantic.dataclasses import dataclass

T = TypeVar("T")
datatypes = []  # The list of defined datatypes


def _datatype(cls: Type[T], *, config: Optional[Type] = None, **kwargs) -> Type[T]:
    """# Inner implementation of `@datatype`"""

    # Get the default `Config` if none is provided
    config = config or OurBaseConfig

    # Convert `cls` to a `pydantic.dataclasses.dataclass`,
    cls = dataclass(cls, config=config, **kwargs)

    # And add it to the list of datatypes
    datatypes.append(cls)
    return cls


def datatype(cls: Optional[Type[T]] = None, **kwargs) -> Type[T]:
    """Register a class as a datatype."""

    # NOTE: the return type here is really, like,
    # `Union[Type[T], Callable[[Type[T]], Type[T]]`
    # But do ya really want that, or just to know it works as a decorator.

    inner = lambda c: _datatype(c, **kwargs)
    if cls is None:
        return inner  # Called with parens, e.g. `@datatype()`
    return inner(cls)  # Called without parens
