""" 
# Hdl21 "PDK" Interface 

Hdl21 "process development kit" (PDK) modules serve to map Hdl21's generic `Primitive` elements 
into technology-specific types. 

This manifests as a "compiler pass" over the Hdl21 circuit-proto tree. 
An `hdl21.proto.Package` is hierarchically traversed, and instances of `hdl21.Primitive`s 
are transformed, typically to process-specific `ExternalModule`s. 

(Full) PDKs are generally not managed as Python packages, but a (rather large) collection of netlists and support files 
which are generally expected to live elsewhere on the file system. 
Hdl21 PDK modules track which such requirements they inject, and insert them as `ExternalSource` requirements. 

The PDK API consists of a single method `compile`, with the signature: 

```python
def compile(src: hdl21.proto.Package) -> hdl21.proto.Package
```

Mutation of the `src` package is allowed, although not recommended (or often terribly helpful).  

Plug-in-style registration of `hdl21.PDK`s makes them available to `hdl21.Generator`s, 
and generally allows for a full program-worth of comprehension of the target process.  
Registering a PDK requires only passing its (Python) module as an argument to the `hdl21pdk.register` function. 

"""

from typing import Callable, Union, Any, Optional
from types import ModuleType

import hdl21 as h


class _PdkManager:
    """The singleton manager of available PDK modules"""

    _the_one = None

    def __new__(cls, *_, **__):
        if cls._the_one is None:
            cls._the_one = super().__new__(cls)
        return cls._the_one

    def __init__(self):
        self.modules = []
        self.default = None


# Create that singleton
_mgr = _PdkManager()


def register(module: ModuleType) -> None:
    """Register the (Python) Module `module` as a PDK"""
    if module not in _mgr.modules:
        if not isinstance(module, ModuleType):
            raise TypeError(f"{module} is not a Python Module")
        if not hasattr(module, "compile"):
            raise TypeError("PDK module must have a compile() method")
        # FIXME: do a buncha type checking here
        compile = module.compile
        _mgr.modules.append(module)
