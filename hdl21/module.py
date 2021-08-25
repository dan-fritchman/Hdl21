"""
# hdl21.module 

The `Module` Module (get it?)
This module primarily defines the core circuit-reuse element `hdl21.Module`. 
It also includes the fun machinery for class-syntax creation of `Module`s, 
enabled by a custom metaclass and its partner custom dictionary, 
which unwind `Module` sub-class-body contents in dataflow order. 
"""
import inspect
from textwrap import dedent
from typing import Any, Optional, List, Union, Dict
from pydantic.dataclasses import dataclass

# Local imports
from .instance import calls_instantiate
from .signal import Signal, Visibility


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

    def __setattr__(self, key: str, val: object):
        """ Set-attribute over-ride, organizing into type-based containers """
        from .signal import Signal, Visibility
        from .instance import Instance, InstArray
        from .interface import InterfaceInstance

        if not getattr(self, "_initialized", False) or key.startswith("_"):
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

        # Type-based organization
        if isinstance(val, Signal):
            val.name = key
            self.namespace[key] = val
            if val.vis == Visibility.PORT:
                self.ports[key] = val
            else:
                self.signals[key] = val
        elif isinstance(val, Instance):
            val.name = key
            self.instances[key] = val
            self.namespace[key] = val
        elif isinstance(val, InstArray):
            val.name = key
            self.instarrays[key] = val
            self.namespace[key] = val
        elif isinstance(val, InterfaceInstance):
            val.name = key
            self.interfaces[key] = val
            self.namespace[key] = val
        else:
            raise TypeError(f"Invalid Module attribute {val} for {self}")

    def add(self, val: Any) -> Any:
        """ Add a named HDL object into one of our internal dictionaries.

        This allows for programmatic insertion of attributes whose names are not legal Python identifiers,
        such as keywords ('in', 'from') and those including invalid characters.
        This method is also the means by which underscore-prefaced attributes are added during elaboration.

        The added object `val` is also provided as the return value, enabling usages such as
        `instance.inp = module.add(h.Input(width=5))` and similar. """

        from .signal import Signal, Visibility
        from .instance import Instance, InstArray
        from .interface import InterfaceInstance

        if not isinstance(val, (Signal, Instance, InstArray, InterfaceInstance)):
            raise TypeError(f"Invalid Module attribute {val} for {self}")
        if not val.name:
            raise RuntimeError(
                f"Invalid anonymous attribute {val} cannot be added to Module {self.name}"
            )
        # Type-based organization
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
    def _interface_ports(self):
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

    Converts a class-body full of Interface-storable attributes to an `hdl21.Module`.
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
    If you'd like atribrary-executing Python-code that creates or manipulates `Modules`,
    you probably want an `hdl21.Generator` instead.

    Temporary variables can be declared inside of the `@module`-decorated class-body,
    so long as they are meet the Python-standard convention for private data:
    name-prefixing with an underscore.
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

    def __call__(self, params) -> "ExternalModuleCall":
        return ExternalModuleCall(module=self, params=params)

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
    # params: Dict[str, Union[int, float, str]]
    params: Any

    @property
    def ports(self) -> dict:
        return self.module.ports
