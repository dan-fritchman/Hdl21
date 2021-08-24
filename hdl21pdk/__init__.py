""" 
# Hdl21 "PDK" Interface 

Hdl21 "process development kit" (PDK) modules serve to map Hdl21's generic `Primitive` elements 
into technology-specific types. 

This manifests as a "compiler pass" over the Hdl21 circuit-proto tree. 
An `hdl21.proto.Package` is hierarchically traversed, and instances of `hdl21.Primitive`s 
are transformed, typically to process-specific `ExternalModule`s. 

(Full) PDKs are generally not managed as Python packages, but a (rather large) collection of netlists and support files 
which are generally expected to live elsewhere on the file system. 
Exporting to such PDK formats therefore requires: 
* (a) Paths to those external files, and 
* (b) Tracking of the target format, as separate files typically define the PDK content for different formats. 

The PDK API consists of one required method `compile` and one optional method `netlist`: 

```python
def compile(src: hdl21.proto.Package) -> hdl21.proto.Package
def netlist(src: hdl21.proto.Package, target: typing.IO, fmt: hdl21.netlist.NetlistFormat) -> None
```

The core method `compile` transforms a process-generic `hdl21.proto.Package` into PDK-specific content. 
This will commonly manifest as replacement of `hdl21.Primitive` instances with PDK-specific `ExternalModule`s. 
Mutation of the `src` package is allowed, although not recommended (or often terribly helpful).  

The `netlist` method (and any likely future methods) use `compile` internally, 
along the way exporting `src` to the file-like object `target`, in netlist-format `fmt`. 
Note providing the netlist-format `fmt` is generally required for sake of including external PDK files, 
typically separated per-format. 

Plug-in-style registration of `hdl21.PDK`s makes them available to `hdl21.Generator`s, 
and generally allows for a full program-worth of comprehension of the target process.  
Registering a PDK requires only passing its (Python) module as an argument to the `hdl21pdk.register` function. 

"""

from typing import Callable, Union, Any, Optional
from types import ModuleType


class _PdkManager:
    """ The singleton manager of available PDK modules """

    _the_one = None

    def __new__(cls, *_, **__):
        if cls._the_one is None:
            cls._the_one = super().__new__(cls)
        return cls._the_one

    def __init__(self):
        self.modules = set()
        self.names = dict()
        self.default = None

    def register(self, module: ModuleType):
        """ Internal registration implementation. 
        Check for validity of `module`, and add it to our set. """
        if module in self.modules:
            return

        # Checks on the PDK `module`
        if not isinstance(module, ModuleType):
            raise TypeError(f"{module} is not a Python Module")
        if not hasattr(module, "compile"):
            raise TypeError("PDK module must have a compile() method")
        # FIXME: do a buncha checking on this method here
        compile = module.compile

        # Checks out. Add it.
        self.modules.add(module)
        self.names[module.__name__] = module


# Create that singleton
_mgr = _PdkManager()


def register(module: ModuleType) -> None:
    """ Register the (Python) Module `module` as a PDK """
    _mgr.register(module)
