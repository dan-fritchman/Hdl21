""" 
# Hdl21 "PDK" Interface 

Hdl21 "process development kit" (PDK) packages provide the interface between the Python HDL and fabricatable process technologies. 
PDK packages typically include: 

* (a) Definitions of technology-specific `ExternalModule`s, commonly including transistors and passive components, and 
* (b) A transformation method for converting genertic `Primitive` elements to the technology-specific `ExternalModule`s.

The latter manifests as a "compiler pass" over the Hdl21 circuit-proto tree. 
An `hdl21.proto.Package` is hierarchically traversed, and instances of `hdl21.Primitive`s 
are transformed, typically to technology-specific `ExternalModule`s. 

The PDK API consists of one required method `compile`: 

```python
def compile(src: hdl21.proto.Package) -> hdl21.proto.Package
```

The core method `compile` transforms a process-generic `hdl21.proto.Package` into PDK-specific content. 
This will commonly manifest as replacement of `hdl21.Primitive` instances with PDK-specific `ExternalModule`s. 
Mutation of the `src` package is allowed, although not recommended (or often terribly helpful).  

Plug-in-style registration of `hdl21.PDK`s makes them available to `hdl21.Generator`s, 
and generally allows for a full program-worth of comprehension of the target process.  
Registering a PDK requires only passing its (Python) module as an argument to the `hdl21pdk.register` function. 
Typical PDKs packages then take the typical form: 

```python
# sample_pdk/__init__.py

import hdl21pdk

# Grab our primary PDK-definition module
from . import sample_pdk

# And register as a PDK module
hdl21pdk.register(sample_pdk)
```

```python
# sample_pdk/sample_pdk.py

import hdl21 as h

# Definitions of PDK modules 
MyMos = h.ExternalModule(name='MyMos', ...) 

# Compilation method 
def compile(src: h.proto.Package) -> h.proto.Package:
    ...

"""

import inspect
from typing import Union
from types import ModuleType

import hdl21 as h


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

    def register(self, module: ModuleType) -> None:
        """ Internal registration implementation. 
        Check for validity of `module`, and add it to our internal structures. """
        if module in self.modules:
            return

        # Checks on the PDK `module`
        if not isinstance(module, ModuleType):
            raise TypeError(f"{module} is not a Python Module")
        if not hasattr(module, "compile"):
            raise TypeError("PDK module must have a compile() method")

        # Do a buncha checking on this method here
        sig = inspect.signature(module.compile)

        args = list(sig.parameters.values())
        if len(args) != 1:
            raise RuntimeError(f"Invalid call signature for {module}.compile: {args}")

        # Extract the parameters-argument type
        paramtype = args[0].annotation
        if paramtype is not h.proto.Package:
            raise RuntimeError(
                f"Invalid call signature for {module}.compile. Argument type must be `h.proto.Package`, not {paramtype}"
            )
        # Validate the return type is also `Package`
        rt = sig.return_annotation
        if rt is not h.proto.Package:
            raise RuntimeError(
                f"Invalid call signature for {module}.compile. Return type must be `h.proto.Package`, not {paramtype}"
            )

        # Checks out. Add it.
        self.modules.add(module)
        self.names[module.__name__] = module


# Create that singleton
_mgr = _PdkManager()


"""
## Public API Methods 
"""


def register(module: ModuleType) -> None:
    """ Register the (Python) Module `module` as a PDK """
    _mgr.register(module)


def compile(src: h.proto.Package) -> h.proto.Package:
    """ Compile using our default PDK module. 
    Raises a `RuntimeError` if there is no unambigous default. """

    if _mgr.default is None:
        compiler = _mgr.default.compile
    elif len(_mgr.modules) == 1:
        compiler = list(_mgr.modules)[0].compile
    elif not len(_mgr.modules):
        raise RuntimeError("No PDK modules registered")
    elif len(_mgr.modules) > 1:
        raise RuntimeError("Multiple PDK modules registered")

    # Run the compiler
    return compiler(src)


def set_default(to: Union[ModuleType, str]) -> None:
    """ Set the default PDK to use when no PDK is specified in a `hdl21.Generator` """
    if isinstance(to, str):
        to = _mgr.names.get(to, None)
        if to is None:
            raise RuntimeError(f"No PDK named {to} registered")
    elif isinstance(to, ModuleType):
        if to not in _mgr.modules:
            raise RuntimeError(f"No PDK named {to} registered")
    else:
        raise TypeError

    # Checks out; set as our default
    _mgr.default = to

