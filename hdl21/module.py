"""
# hdl21.module 
The `Module` module (get it?)

This module primarily defines the core circuit-reuse element `hdl21.Module`. 
It also includes the fun machinery for class-syntax creation of `Module`s, 
particularly the `@module` (lower-case) decorator-function. 
"""

import inspect
from textwrap import dedent
from typing import Any, Optional, List, Union, Dict, get_args
from pydantic.dataclasses import dataclass

# Local imports
from .signal import Signal, Visibility
from .instance import calls_instantiate, Instance, InstArray
from .interface import InterfaceInstance

# Type-alias for HDL objects storable as `Module` attributes
ModuleAttr = Union[Signal, Instance, InstArray, InterfaceInstance]


def _is_module_attr(val: Any) -> bool:
    """ Boolean indication of whether `val` is a valid `hdl21.Module` attribute. """
    return isinstance(val, get_args(ModuleAttr))


@calls_instantiate
class Module:
    """
    # Module
    The central element of hardware re-use.
    """

    def __init__(self, *, name: Optional[str] = None):
        self.name = name
        self.ports = dict()
        self.signals = dict()
        self.instances = dict()
        self.instarrays = dict()
        self.interfaces = dict()
        self.namespace = dict()  # Combination of all these
        for fr in inspect.stack():
            # Find the first frame not from *this* file
            # Sometimes this will be a Generator. That's OK, they'll figure it out.
            pymod = inspect.getmodule(fr[0])
            if pymod.__file__ != __file__:
                break
        self._pymodule = pymod  # Reference to the (Python) module where called
        self._importpath = None  # Optional field set by importers
        self._initialized = True

    def __setattr__(self, key: str, val: Any) -> None:
        """ Set-attribute over-ride, organizing into type-based containers """

        if not getattr(self, "_initialized", False) or key.startswith("_"):
            # Bootstrapping phase. Pass along to "regular" setattr.
            return super().__setattr__(key, val)

        # Protected attrs - the internal dicts
        banned = [
            "ports",
            "signals",
            "instances",
            "namespace",
            "add",
            "_interface_ports",
            "_pymodule",
            "_importpath",
            "_initialized",
        ]
        if key in banned:
            raise RuntimeError(
                f"Error attempting to over-write protected attribute {key} of Module {self}"
            )
        # Special case(s)
        if key == "name":
            return super().__setattr__(key, val)

        if not _is_module_attr(val):
            raise TypeError(f"Invalid Module attribute {val} for {self}")

        # Checks out! Name `val` and add it to our type-based containers.
        val.name = key
        _ = self._add(val)
        return None

    def add(self, val: ModuleAttr, *, name: Optional[str] = None) -> ModuleAttr:
        """ Add a named HDL object into one of our internal dictionaries.

        This allows for programmatic insertion of attributes whose names are not legal Python identifiers,
        such as keywords ('in', 'from') and those including invalid characters.

        The added object `val` is also provided as the return value, enabling chaining-style usages such as
        ```python
        instance.inp = MyModule.add(h.Input(name="in", width=5))
        ``` 
        and similar. """

        if not _is_module_attr(val):
            raise TypeError(f"Invalid Module attribute {val} for {self}")

        # Now sort out naming. We get two name-sources:
        # (a) the function-argument `name` and (b) the value's `name` attribute.
        # One or the other (and not both) must be set.
        if name is None and val.name is None:
            raise RuntimeError(
                f"Invalid anonymous attribute {val} cannot be added to Module {self.name}"
            )
        if name is not None and val.name is not None:
            raise RuntimeError(
                f"Conflicting names {name} and {val.name} cannot be added to Module {self.name}"
            )
        if name is not None:
            val.name = name

        # Now `val.name` is set appropriately.
        # Add it to our type-based containers, and return it.
        return self._add(val)

    def _add(self, val: ModuleAttr) -> ModuleAttr:
        """ Internal `add` and `setattr` implementation. 
        Primarily sort `val` into one of our type-based containers. """

        if isinstance(val, Signal):
            self.namespace[val.name] = val
            if val.vis == Visibility.PORT:
                self.ports[val.name] = val
            else:
                self.signals[val.name] = val
        elif isinstance(val, Instance):
            self.instances[val.name] = val
            self.namespace[val.name] = val
        elif isinstance(val, InstArray):
            self.instarrays[val.name] = val
            self.namespace[val.name] = val
        elif isinstance(val, InterfaceInstance):
            self.interfaces[val.name] = val
            self.namespace[val.name] = val
        else:
            raise TypeError(f"Invalid Module attribute {val} for {self}")

        # And return our newly-added attribute
        return val

    def get(self, name: str) -> Optional[ModuleAttr]:
        """ Get module-attribute `name`. Returns `None` if not present. 
        Note unlike Python built-ins such as `getattr`, `get` returns solely 
        from the HDL namespace-worth of `ModuleAttr`s. """
        ns = self.__getattribute__("namespace")
        return ns.get(name, None)

    def __getattr__(self, key: str) -> Any:
        """ Include our namespace-worth of HDL objects in dot-access retrievals """
        ns = self.__getattribute__("namespace")
        if key in ns:
            return ns[key]
        return object.__getattribute__(self, key)

    def __init_subclass__(cls, *_, **__):
        """ Sub-Classing Disable-ization """
        raise RuntimeError(
            dedent(
                f"""\
                Error attempting to create {cls.__name__}
                Sub-Typing hdl21.Module is not supported. """
            )
        )

    def __repr__(self) -> str:
        if self.name:
            return f"Module(name={self.name})"
        return f"Module(_anon_)"

    @property
    def _interface_ports(self) -> dict:
        """ Port-Exposed Interface Instances """
        return {name: intf for name, intf in self.interfaces.items() if intf.port}

    def _defpath(self) -> str:
        """ Helper for exporting. 
        Returns a string representing "where" this module was defined. 
        This is generally one of a few things: 
        * If "normally" defined via Python code, it's the Python module path 
        * If *imported*, it's the path inferred during import """
        if self._importpath:  # Imported. Return the period-separated import path.
            return ".".join(self._importpath)
        # Defined the old fashioned way. Use the Python module name.
        return self._pymodule.__name__


def module(cls: type) -> Module:
    """
    # Module Definition Decorator

    Converts a class-body full of Module-storable attributes to an `hdl21.Module`.
    Example Usage:

    ```python
    import hdl21 as h

    @h.module
    class M1:
        d = h.Port()
        e = h.Signal()

    @h.module
    class M2:
        q = h.Signal()
        i = M1(d=q)
    ```

    `hdl21.Modules` are strongly-typed containers of other hardware objects:
    * `Signals` and `Ports`
    * Instances of other `Modules`
    * Structured connections via `Interfaces`

    Attempts to set module attributes of any other types will raise a `TypeError`.
    Notably this includes any behavioral elements implemented by Python functions.
    If you'd like arbitrary-executing Python-code that creates or manipulates `Modules`,
    you probably want an `hdl21.Generator` instead.

    Temporary variables can be declared inside of the `@module`-decorated class-body,
    so long as they are meet the Python convention for private data: name-prefixing with an underscore.
    These temporary variables are *not* propagated along as members of the `Module`.
    """

    if cls.__bases__ != (object,):
        raise RuntimeError(f"Invalid @hdl21.module inheriting from {cls.__bases__}")

    # Create the Module object
    module = Module(name=cls.__name__)

    dunders = dict()
    unders = dict()

    # Take a lap through the class dictionary, type-check everything and assign relevant attributes to the interface
    for key, val in cls.__dict__.items():
        if key.startswith("__"):
            dunders[key] = val
        elif key.startswith("_"):
            unders[key] = val
        else:
            setattr(module, key, val)
    # And return the Module
    return module


@dataclass
class ExternalModule:
    """
    # External Module

    Wrapper for circuits defined outside Hdl21, such as:
    * Inclusion of existing SPICE or Verilog netlists
    * Foundry or technology-specific primitives

    Unlike `Modules`, `ExternalModules` include parameters to support legacy HDLs.
    Said parameters may only take on a limited number of datatypes,
    and may not be nested.
    Parameter type-requirements *are not* stored by `ExternalModules`.
    Calling them to create a parametrized instance stores a largely arbitrary
    dictionary of params.
    """

    name: str
    desc: str
    port_list: List[Signal]
    domain: Optional[str] = None
    # FIXME: do we want an optional parameter-types type-thing

    def __post_init_post_parse__(self):
        """After type-checking, do some more checks on values"""
        for p in self.port_list:
            if not p.name:
                raise ValueError(f"Unnamed Primitive Port {p} for {self.name}")
            if p.vis != Visibility.PORT:
                raise ValueError(
                    f"Invalid Primitive Port {p.name} on {self.name}; must have PORT visibility"
                )

    def __call__(self, **kwargs) -> "ExternalModuleCall":
        return ExternalModuleCall(module=self, params=kwargs)

    @property
    def ports(self) -> dict:
        return {p.name: p for p in self.port_list}


@calls_instantiate
@dataclass
class ExternalModuleCall:
    """External Module Call
    A combination of an `ExternalModule` and its Parameter-values,
    typically generated by calling the Module."""

    module: ExternalModule
    params: Dict[str, Union[int, float, str]]

    @property
    def ports(self) -> dict:
        return self.module.ports
