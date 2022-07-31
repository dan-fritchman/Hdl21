""" 
# Hdl21 Hierarchical Instances 

Create instances of Modules, Generators, and Primitives in a hierarchy
"""

# Std-Lib Imports
from typing import Optional, Any, Dict, Set
from textwrap import dedent

# Local imports
from .source_info import source_info, SourceInfo
from .attrmagic import init
from .connect import Connectable, is_connectable


@init
class _Instance:
    """Shared base class for Instance-like types (Instance, InstanceArray)"""

    def __init__(
        self, of: "Instantiable", *, name: Optional[str] = None,
    ):
        from .instantiable import Instantiable, is_instantiable
        from .portref import PortRef

        if not is_instantiable(of):
            raise RuntimeError(f"Invalid Instance of {of}")

        self.name: Optional[str] = name
        self.of: "Instantiable" = of
        self.conns: Dict[str, "Connectable"] = dict()
        # References given out to our ports, generally via `__getattr__`
        self._portrefs: Dict[str, "PortRef"] = dict()
        # References to our connections, generally via `connect`
        self._connrefs: Dict[str, "PortRef"] = dict()

        self._parent_module: Optional["Module"] = None  # Instantiating module
        self._elaborated: bool = False
        self._source_info: Optional[SourceInfo] = source_info(get_pymodule=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name} of={self.of})"

    @property
    def _resolved(self,) -> Optional["Instantiable"]:
        """Property to retrieve the Instance's resolved Module, if complete.
        Returns `None` if unresolved."""
        from .generator import GeneratorCall

        if isinstance(self.of, GeneratorCall):
            return self.of.result
        return self.of

    def __getattr__(self, key: str) -> Any:
        """Port access by getattr"""
        if not self.__getattribute__("_initialized") or key.startswith("_"):
            # Bootstrapping phase: do regular getattrs to get started
            return object.__getattribute__(self, key)

        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__getattribute__(self, key)

        # After elaboration, the fancy PortRef creation below goes away. Only return ready-made connections.
        if self.__getattribute__("_elaborated"):
            # Pull from the `conns` dict.
            conns = self.__getattribute__("conns")
            if key in conns.keys():
                return conns[key]
            raise AttributeError(f"No attribute {key} for {self}")

        # Fell through all those cases. Fancy `PortRef` generation time!
        # Return a `PortRef`, creating one if necessary.
        return _get_portref(self, key)

    def __call__(self, **kwargs) -> "_Instance":
        """Connect-by-call"""
        for key, val in kwargs.items():
            self.connect(key, val)
        # Don't forget to retain ourselves at the call-site!
        return self

    def __setattr__(self, key: str, val: Any) -> None:
        """Connect-by-setattr"""
        if not getattr(self, "_initialized", False) or key.startswith("_"):
            # Bootstrapping phase: do regular setattrs to get started
            return object.__setattr__(self, key, val)
        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__setattr__(self, key, val)
        _ = self.connect(key, val)  # Discard the returned `self`
        return None

    def connect(self, portname: str, conn: Connectable) -> "_Instance":
        """Connect `conn` to port (name) `portname`.
        Called by both by-call and by-assignment convenience methods, and usable directly.
        Direct calls to `connect` will generally be required for ports with otherwise illegal names,
        e.g. Python language keywords (`in`, `from`, etc.),
        or Hdl21 internal "keywords" (`name`, `ports`, `signals`, etc.).
        Returns `self` to aid in method-chaining use-cases."""
        from .bundle import AnonymousBundle

        if isinstance(conn, Dict):
            # Special-case dictionaries of connectables into Anon Bundles
            conn = AnonymousBundle(**conn)
        if not is_connectable(conn):
            raise TypeError(f"{self} attempting to connect non-connectable {conn}")

        # The main event: actually stick `conn` in the `conns` dict
        if portname in self.conns:
            # Replace and disconnect any prior connection
            self.replace(portname, conn)
        else:
            self.conns[portname] = conn

        # And return `self` to aid in method-chaining use-cases
        return self

    def disconnect(self, portname: str) -> Connectable:
        """Disconnect the port named `portname`.
        Returns the formerly-connected `Connectable`.
        Raises a KeyError if the port is not connected."""

        return self.conns.pop(portname)

    def replace(self, portname: str, conn: Connectable) -> Connectable:
        """
        Replace the connection to `portname` with `conn`.
        Returns the formerly-connected `Connectable`.
        Raises a KeyError if the port is not connected.

        The `replace` method is functionally identical to serial calls to `disconnect` and `connect`,
        but allows for in-place modification of the `conns` dict, e.g. while iterating over its items.
        """

        # Get a reference to the old connection in the `conns` dict, without removing it
        old = self.conns[portname]
        # And replace it in the `conns` dict
        self.conns[portname] = conn
        return old


def _mult(inst: "Instance", other: int) -> "InstanceArray":
    """Instance by integer multiplication.
    Creates an Instance Array of size `other`."""
    if not isinstance(other, int):
        return NotImplemented
    return _to_array(inst=inst, num=other)


class Instance(_Instance):
    """Hierarchical Instance of another Module or Generator"""

    __mul__ = __rmul__ = _mult  # Apply `_mult` on both left and right

    _specialcases = [
        "name",
        "of",
        "conns",
        "connect",
        "disconnect",
        "replace",
    ]

    def __init__(self, *_, **__):
        # Just call the base-class constructor, and set the `_initialized` flag.
        # The need to do so is just an enabler for other sub-classes to add constructor action.
        super().__init__(*_, **__)
        self._initialized = True


class InstanceBundle(_Instance):
    """Named set of Instances, paired with a Signal Bundle."""

    # The paired signal-Bundle type. Note this is a class-level attribute.
    bundle: Optional["Bundle"] = None

    _specialcases = [
        "name",
        "of",
        "conns",
        "connect",
        "disconnect",
        "replace",
    ]

    def __init__(self, *_, **__):
        # Just call the base-class constructor, and set the `_initialized` flag.
        # The need to do so is just an enabler for other sub-classes to add constructor action.
        super().__init__(*_, **__)
        self._initialized = True


def InstanceBundleType(name: str, bundle: "Bundle", doc: Optional[str] = None) -> type:
    """Create a new sub-class of `InstanceBundle`, tied to Bundle-type `bundle`."""

    from .bundle import Bundle

    if not isinstance(name, str):
        raise TypeError
    if not isinstance(bundle, Bundle):
        raise TypeError

    # Set a default doc-string
    doc = doc or f"`InstanceBundle` type `{name}` of `Bundle` `{bundle.name}`"
    doc = dedent(doc)

    # Create and return the new type
    return type(name, (InstanceBundle,), {"bundle": bundle, "__doc__": doc})


class InstanceArray(_Instance):
    """Array of `n` Instances"""

    _specialcases = [
        "name",
        "of",
        "conns",
        "portref",
        "portrefs",
        "connect",
        "disconnect",
        "replace",
    ]

    def __init__(
        self, of: "Instantiable", n: int, name: Optional[str] = None,
    ):
        super().__init__(of=of, name=name)
        self.n = n
        self._initialized = True

    def __getitem__(self, idx: int):
        return RuntimeError(f"Illegal indexing into Array {self}")

    def __setitem__(self, _idx: Any, _val: Any):
        return RuntimeError(f"Illegal indexing into Array {self}")


""" 
Module-level functions 
These could be instance methods, but are kept here to minimally pollute their namespaces.
"""


def _to_array(inst: Instance, num: int) -> InstanceArray:
    """Create an Instance Array from an Instance"""
    # Several contraints asserted here which may eventually be relaxed.
    # * No port-references (yet)
    # * Not a member of a module (yet)
    if len(inst._portrefs) > 0:
        msg = f"Cannot convert Instance {inst} with outstanding port-references {inst._portrefs} to Array"
        raise RuntimeError(msg)
    if inst._parent_module is not None:
        msg = f"Cannot convert Instance {inst} already inserted in Module {inst._parent_module} to Array"
        raise RuntimeError(msg)

    # Checks out. Create the array.
    return InstanceArray(of=inst.of, n=num, name=inst.name)(**inst.conns)


def _get_portref(self: _Instance, key: str) -> "PortRef":
    """Return a port-reference to name `key`, creating it if necessary."""
    from .portref import PortRef

    # Check in our existing port-references
    portrefs = self.__getattribute__("_portrefs")
    if key in portrefs:
        return portrefs[key]

    # New reference; create, add, and return it
    port_ref = PortRef(inst=self, portname=key)
    portrefs[key] = port_ref
    return port_ref


""" 
Instantiation Decorator 
"""


def calls_instantiate(cls: type) -> type:
    """# Calls Instantiate
    Decorator which adds 'calls produce `hdl21.Instance`s' functionality.
    Added to `Module`, `GeneratorCall`, and everything else that is `Instantiable`."""

    def __call__(self, **kwargs) -> Instance:
        """Calls Create `hdl21.Instances`,
        and pass any (keyword-only) arguments to said `Instances`,
        generally to connect-by-call."""
        return Instance(of=self)(**kwargs)

    # Check for an existing __call__ method, and if there is one, bail
    if "__call__" in cls.__dict__:
        msg = f"Hdl21 Internal Error: Invalid conflict between `calls_instantiate` decorator and explicit `__call__` method on {cls}"
        raise RuntimeError(msg)

    cls.__call__ = __call__
    return cls


"""
Selected star-exports 
Notably excludes the base class, and module-level functions
"""
__all__ = [
    "Instance",
    "InstanceArray",
    "InstanceBundle",
    "InstanceBundleType",
    "calls_instantiate",
]
