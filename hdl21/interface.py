from textwrap import dedent
from enum import Enum, EnumMeta
from typing import Optional, Union, Any, get_args

from .instance import connects, connectable
from .signal import Signal


@connects
@connectable
class InterfaceInstance:
    """ Instance of an Interface, 
    Generally in a Module or another Interface """

    _specialcases = [
        "name",
        "of",
        "port",
        "role",
        "src",
        "dest",
        "conns",
        "portrefs",
        "_elaborated",
        "_initialized",
    ]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        of: "Interface",
        port: bool = False,
        role: Optional[Enum] = None,
        src: Optional[Enum] = None,
        dest: Optional[Enum] = None,
    ):
        self.name = name
        self.of = of
        self.port = port
        self.role = role
        self.src = src
        self.dest = dest
        self.conns = dict()
        self.portrefs = dict()
        self._elaborated = False
        self._initialized = True

    @property
    def _resolved(self) -> "Interface":
        return self.of


# Type-alias for HDL objects storable as `Module` attributes
InterfaceAttr = Union[Signal, InterfaceInstance]


def _is_interface_attr(val: Any) -> bool:
    """ Boolean indication of whether `val` is a valid `hdl21.Interface` attribute. """
    return isinstance(val, get_args(InterfaceAttr))


class Interface:
    """ 
    # hdl21 Interface
    
    Interfaces are structured hierarchical connection objects which include Signals and other Interfaces. 
    """

    def __init__(self, *, name=None):
        self.name = name
        self.roles = None
        self.signals = dict()
        self.interfaces = dict()
        self.namespace = dict()  # Combination of all these
        self._elaborated = False
        self._initialized = True

    def __setattr__(self, key: str, val: object):
        """ Set-attribute over-ride, organizing into type-based containers """
        from .signal import Signal

        if not getattr(self, "_initialized", False) or key.startswith("_"):
            return super().__setattr__(key, val)

        # Protected attrs - the internal dicts
        banned = ["signals", "interfaces", "namespace"]
        if key in banned:
            raise RuntimeError(
                f"Error attempting to over-write protected attribute {key} of Interface {self}"
            )
        # Special case(s)
        if key == "name":
            return super().__setattr__(key, val)
        if key == "roles":
            if not isinstance(val, EnumMeta):
                raise TypeError(f"Interface roles must be an `enum.Enum`")
            return super().__setattr__(key, val)

        # Type-based organization
        if isinstance(val, Signal):
            val.name = key
            self.namespace[key] = val
            self.signals[key] = val
        elif isinstance(val, InterfaceInstance):
            val.name = key
            self.interfaces[key] = val
            self.namespace[key] = val
        else:
            raise TypeError(f"Invalid Interface attribute {val} for {self}")

    def __getattr__(self, key):
        ns = self.__getattribute__("namespace")
        if key in ns:
            return ns[key]
        return object.__getattribute__(self, key)

    def __call__(self, **kwargs):
        """ Calls to Interfaces return Interface Instances """
        return InterfaceInstance(of=self, **kwargs)

    def __init_subclass__(cls, *_args, **_kwargs):
        """ Sub-Classing Disable-ization """
        raise RuntimeError(
            dedent(
                f"""\
                Error attempting to create {cls.__name__}
                Sub-Typing hdl21.Interface is not supported. """
            )
        )

    def add(self, val: InterfaceAttr, *, name: Optional[str] = None) -> InterfaceAttr:
        raise NotImplementedError

    def get(self, name: str) -> Optional[InterfaceAttr]:
        """ Get module-attribute `name`. Returns `None` if not present. 
        Note unlike Python built-ins such as `getattr`, `get` returns solely 
        from the HDL namespace-worth of `InterfaceAttr`s. """
        ns = self.__getattribute__("namespace")
        return ns.get(name, None)

    @property
    def Roles(self):
        # Roles often look like a class, so they have a class-style name-accessor
        return self.roles


def interface(cls: type) -> Interface:
    """ # Interface Definition Decorator 
    
    Converts a class-body full of Interface-storable attributes (Signals, other Interfaces) to an `hdl21.Interface`. 
    Example Usage: 

    ```python
    import hdl21 as h

    @h.interface
    class Diff:
        p = h.Signal()
        n = h.Signal()

    @h.interface
    class DisplayPort:
        main_link = Diff()
        aux = h.Signal()
    ```

    Interfaces may also define a `Roles` enumeration, inline within this class-body. 
    `Roles` are optional pieces of enumerated endpoint-labels which aid in dictating `Signal` directions. 
    Each `Signal` accepts optional source (`src`) and destination (`dst`) fields which (if set) must be one of these roles. 
    
    ```python
    import hdl21 as h
    from enum import Enum, auto

    @h.interface
    class HasRoles:
        class Roles(Enum):
            HOST = auto()
            DEVICE = auto()

        tx = h.Signal(src=Roles.HOST, dest=Roles.DEVICE)
        rx = h.Signal(src=Roles.DEVICE, dest=Roles.HOST)
    ```

    """
    if cls.__bases__ != (object,):
        raise RuntimeError(f"Invalid @hdl21.interface inheriting from {cls.__bases__}")

    # Create the Interface object
    intf = Interface(name=cls.__name__)

    protected_names = ["signals", "interfaces"]
    dunders = dict()
    unders = dict()

    # Take a lap through the class dictionary, type-check everything and assign relevant attributes to the interface
    for key, val in cls.__dict__.items():
        if key in protected_names:
            raise RuntimeError(f"Invalid field name {key} in interface {cls}")
        elif key.startswith("__"):
            dunders[key] = val
        elif key.startswith("_"):
            unders[key] = val
        elif key == "Roles":
            # Special-case the upper-cased `Roles`, as it'll often be a class-def
            setattr(intf, "roles", val)
        else:
            setattr(intf, key, val)
    # And return the interface
    return intf
