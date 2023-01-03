""" 
# Hdl21 PDK Interface

Hdl21 "process development kit" (PDK) packages provide the bundle between the Python HDL and fabricatable process technologies. 
PDK packages typically include: 

* (a) Definitions of technology-specific `ExternalModule`s, commonly including transistors and passive components, and 
* (b) A transformation method for converting genertic `Primitive` elements to the technology-specific `ExternalModule`s.

The latter manifests as a "compiler pass" over the Hdl21 circuit-proto tree. 
An Hdl21 design hierarchically traversed and instances of `hdl21.Primitive`s 
are transformed, typically to technology-specific `ExternalModule`s. 

The PDK API consists of one required method `compile`: 

```python
def compile(src: Elaboratables) -> None
```

The core method `compile` transforms a process-generic design hierarchy into PDK-specific content. 
This will commonly manifest as replacement of `hdl21.Primitive` instances with PDK-specific `ExternalModule`s. 

The `Elaboratables` union type which serves as the input of `compile` can be any of: 

* An `hdl21.Module`
* A call to an `hdl21.Generator`
* Lists thereof

A typical implementation of `compile`, shown in the `hdl21.pdk.sample_pdk` package, is to call the base class `visit_elaboratables` 
method on a `Walker` subclass which implements the desired PDK transformations. For example: 

```python
def compile(src: h.Elaboratables) -> None:
    # Compile `src` to the Sample technology 
    return SamplePdkWalker().visit_elaboratables(src)
```

## Plug-in System 

Plug-in-style registration of `hdl21.PDK`s makes them available to `hdl21.Generator`s, 
and generally allows for a full program-worth of comprehension of the target process.  
Registering a PDK requires only passing its (Python) module as an argument to the `hdl21.pdk.register` function. 
Typical PDKs packages then take the typical form: 

```python
from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import sample_pdk

# And register as a PDK module
register(sample_pdk)
```

```python
# sample_pdk/sample_pdk.py

import hdl21 as h

# Definitions of PDK modules 
MyMos = h.ExternalModule(name='MyMos', ...) 

# Compilation method 
def compile(src: h.Elaboratables) -> h.Elaboratables:
    ...

"""

import inspect
from typing import Optional, Union
from types import ModuleType

from ..elab import Elaboratables


class _PdkManager:
    """The "private" singleton manager of available PDK modules"""

    _the_one = None

    def __new__(cls, *_, **__):
        if cls._the_one is None:
            cls._the_one = super().__new__(cls)
        return cls._the_one

    def __init__(self):
        self.modules = set()
        self.names = dict()
        self.default = None


# Create that singleton
_mgr = _PdkManager()


"""
## Public API Methods 
"""


def register(module: ModuleType) -> None:
    """Register the (Python) Module `module` as a PDK"""
    if module in _mgr.modules:
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
    if paramtype is not Elaboratables:
        msg = f"Invalid call signature for {module}.compile. Argument type must be `hdl21.Elaboratables`, not {paramtype}"
        raise RuntimeError(msg)

    # Validate the return type is also `Package`
    rt = sig.return_annotation
    if rt not in (None, type(None)):
        msg = f"Invalid call signature for {module}.compile. Return type must be `None`, not {paramtype}"
        raise RuntimeError(msg)

    # Checks out. Add it.
    _mgr.modules.add(module)
    _mgr.names[module.__name__] = module


def compile(
    src: Elaboratables, pdk: Optional[Union[str, ModuleType]] = None
) -> Elaboratables:
    """
    Compile to a target PDK.

    Uses the optional `pdk` argument as a target, if provided and valid.
    Otherwise uses the default PDK module.
    Raises a `RuntimeError` if there is no unambigous default.
    """
    if pdk is None:
        pdk = default()
    elif isinstance(pdk, str):
        # Grab by-name from our registered names-dict
        pdk = _mgr.names.get(pdk, None)
        if pdk is None:
            msg = f"No PDK named {pdk}"
            raise RuntimeError(msg)
    elif isinstance(pdk, ModuleType):
        # Ensure that `pdk` is registered and checked as a valid PDK module
        _mgr.register(pdk)

    if pdk is None:  # Check for no-default-available cases
        if not len(_mgr.modules):
            raise RuntimeError("No PDK modules registered")

        msg = f"Multiple ({len(_mgr.modules)}) PDK modules registered: [\n"
        for m in _mgr.modules:
            msg += "\t" + str(m) + "\n"
        msg += "] \n"
        msg += f"Set one as the default via `hdl21.pdk.set_default()` (or remove all others) to use `h.pdk.compile()`."
        raise RuntimeError(msg)

    # Run the compiler
    return pdk.compile(src)


def set_default(to: Union[ModuleType, str]) -> None:
    """Set the default PDK to use when no PDK is specified in a `hdl21.Generator`"""

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


def default() -> Optional[ModuleType]:
    """Retrieve the default PDK plug-in, if there is an unambiguous one set up."""

    if _mgr.default is not None:
        return _mgr.default
    if len(_mgr.modules) == 1:
        # Get the only element from the set
        return next(iter(_mgr.modules))
    return None
