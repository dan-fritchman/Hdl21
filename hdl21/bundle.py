""" 
# `hdl21.Bundle` and Related Classes 

Structured connection objects, instances thereof, and associated utilities.
"""

from enum import Enum, EnumMeta
from typing import Optional, Union, Any, Dict, Set, List, ClassVar

# Local Imports
from .attrmagic import init
from .connect import connectable, is_connectable
from .sliceable import sliceable
from .concat import concatable
from .signal import Signal


def getattr_bundle_refs(cls: type) -> type:
    """Decorator to add the "__getattr__ generates BundleRefs" functionality to `cls`.
    Adds the `_bundle_ref` method and `__getattr__` access to it."""

    # First check and fail if any of the methods to be defined here are already defined elsewhere
    defined_here = ["__getattr__"]
    for key in defined_here:
        if key in cls.__dict__:
            msg = f"Invalid modification of {cls} with `@getattr_bundle_refs`: {key} is already defined."
            raise RuntimeError(msg)

    def __getattr__(self, key: str) -> Any:
        """BundleRef access by getattr"""
        if key.startswith("_") or not self.__getattribute__("_initialized"):
            # Bootstrapping phase: do regular getattrs to get started
            return object.__getattribute__(self, key)

        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__getattribute__(self, key)

        # After elaboration, the fancy BundleRef creation below goes away. Only return ready-made refs.
        if self.__getattribute__("_elaborated"):
            refs = self.__getattribute__("refs_to_me")
            if key in refs.keys():
                return refs[key]
            raise AttributeError(f"No attribute {key} for {self}")

        # Fell through all those cases. Fancy `BundleRef` generation time!
        # Return a `BundleRef`, creating one if necessary.
        return _bundle_ref(self, key)

    cls.__getattr__ = __getattr__
    cls.__getattr_bundle_refs__ = True

    # And don't forget to return it!
    return cls


def has_getattr_bundle_refs(obj: Any) -> bool:
    """Boolean indication of "getattr bundle refs" functionality"""
    return getattr(obj, "__getattr_bundle_refs__", False)


@getattr_bundle_refs
@connectable
@init
class BundleInstance:
    """# Instance of a `Bundle`
    Generally in a `Module` or another `Bundle`"""

    _specialcases = [
        "name",
        "of",
        "port",
        "role",
        "src",
        "dest",
        "desc",
        "refs_to_me",
    ]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        of: "Bundle",
        port: bool = False,
        role: Optional[Enum] = None,
        src: Optional[Enum] = None,
        dest: Optional[Enum] = None,
        desc: Optional[str] = None,
    ):
        self.name = name
        self.of = of
        self.port = port
        self.role = role
        self.src = src
        self.dest = dest
        self.desc = desc
        # References handed out to our children
        self.refs_to_me: Dict[str, "BundleRef"] = dict()
        # Connected port references
        self._connected_ports: Set["PortRef"] = set()
        self._parent_module: Optional["Module"] = None
        self._elaborated = False
        self._initialized = True

    @property
    def _resolved(self) -> "Bundle":
        return self.of

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name} of={self.of})"


# Type-alias for HDL objects storable as `Module` attributes
BundleAttr = Union[Signal, BundleInstance]


def is_bundle_attr(val: Any) -> bool:
    """Boolean indication of whether `val` is a valid `hdl21.Bundle` attribute."""
    return isinstance(val, BundleAttr.__args__)


@init
class Bundle:
    """
    # hdl21 Bundle

    Bundles are structured hierarchical connection objects which include Signals and other Bundles.
    """

    def __init__(self, *, name=None):
        self.name = name
        self.roles = None
        self.signals = dict()
        self.bundles = dict()
        self.namespace = dict()  # Combination of all these
        self._elaborated = False
        self._initialized = True

    def __setattr__(self, key: str, val: object):
        """Set-attribute over-ride, organizing into type-based containers"""
        from .signal import Signal

        if not getattr(self, "_initialized", False) or key.startswith("_"):
            return super().__setattr__(key, val)

        # Protected attrs - the internal dicts
        banned = ["signals", "bundles", "namespace"]
        if key in banned:
            msg = f"Error attempting to over-write protected attribute {key} of Bundle {self}"
            raise RuntimeError(msg)
        # Special case(s)
        if key == "name":
            return super().__setattr__(key, val)
        if key == "roles":
            if not isinstance(val, EnumMeta):
                raise TypeError(f"Bundle roles must be an `enum.Enum`")
            return super().__setattr__(key, val)

        # Type-based organization
        if isinstance(val, Signal):
            val.name = key
            self.namespace[key] = val
            self.signals[key] = val
        elif isinstance(val, BundleInstance):
            val.name = key
            self.bundles[key] = val
            self.namespace[key] = val
        else:
            raise TypeError(f"Invalid Bundle attribute {val} for {self}")

    def __getattr__(self, key):
        ns = self.__getattribute__("namespace")
        if key in ns:
            return ns[key]
        return object.__getattribute__(self, key)

    def __call__(self, **kwargs):
        """Calls to Bundles return Bundle Instances"""
        return BundleInstance(of=self, **kwargs)

    def __init_subclass__(cls, *_args, **_kwargs):
        """Sub-Classing Disable-ization"""
        msg = f"Error attempting to create {cls.__name__}. Sub-Typing hdl21.Bundle is not supported."
        raise RuntimeError(msg)

    def add(self, val: BundleAttr, *, name: Optional[str] = None) -> BundleAttr:
        raise NotImplementedError  # FIXME!

    def get(self, name: str) -> Optional[BundleAttr]:
        """Get module-attribute `name`. Returns `None` if not present.
        Note unlike Python built-ins such as `getattr`, `get` returns solely
        from the HDL namespace-worth of `BundleAttr`s."""
        ns = self.__getattribute__("namespace")
        return ns.get(name, None)

    @property
    def Roles(self):
        """Roles-Enumeration Accessor Property"""
        # Roles often look like a class, so they have a class-style name-accessor
        return self.roles

    def __repr__(self) -> str:
        if self.name:
            return f"Bundle(name={self.name})"
        return f"Bundle(_anon_)"


def bundle(cls: type) -> Bundle:
    """# Bundle Definition Decorator

    Converts a class-body full of Bundle-storable attributes (Signals, other Bundles) to an `hdl21.Bundle`.
    Example Usage:

    ```python
    import hdl21 as h

    @h.bundle
    class Diff:
        p = h.Signal()
        n = h.Signal()

    @h.bundle
    class DisplayPort:
        main_link = Diff()
        aux = h.Signal()
    ```

    Bundles may also define a `Roles` enumeration, inline within this class-body.
    `Roles` are optional pieces of enumerated endpoint-labels which aid in dictating `Signal` directions.
    Each `Signal` accepts optional source (`src`) and destination (`dst`) fields which (if set) must be one of these roles.

    ```python
    import hdl21 as h
    from enum import Enum, auto

    @h.bundle
    class HasRoles:
        class Roles(Enum):
            HOST = auto()
            DEVICE = auto()

        tx = h.Signal(src=Roles.HOST, dest=Roles.DEVICE)
        rx = h.Signal(src=Roles.DEVICE, dest=Roles.HOST)
    ```

    Bundle roles may be set by defining either a (lower case) `roles` or an
    (upper case) `Roles` attribute within the class body.
    In the resultant `Bundle` they will be accessible as either.
    """
    if cls.__bases__ != (object,):
        raise RuntimeError(f"Invalid @hdl21.bundle inheriting from {cls.__bases__}")

    # Create the Bundle object
    bundle = Bundle(name=cls.__name__)

    protected_names = ["signals", "bundles"]
    # Any class-body content that isn't a `ModuleAttr` will be "forgotten" from the `Module` definition.
    # This can nonetheless be handy for defining intermediate values upon which the ultimate Module attributes depend.
    forgetme: List[Any] = list()

    # Take a lap through the class dictionary, type-check everything and assign relevant attributes to the bundle
    for key, val in cls.__dict__.items():
        if key in protected_names:
            raise RuntimeError(f"Invalid field name {key} in bundle {cls}")
        elif key == "roles" or key == "Roles":
            # Special-case the upper-cased `Roles`, as it'll often be a class-def
            setattr(bundle, "roles", val)
        elif is_bundle_attr(val):
            setattr(bundle, key, val)
        else:  # Add to the forget-list
            forgetme.append(val)

    # And return the bundle
    return bundle


@connectable
class AnonymousBundle:
    """# Anonymous Connection Bundle
    Commonly used for "collecting" Signals into `h.Bundle`s,
    or for re-jiggering connections between `h.Bundle`s."""

    def __init__(self, **kwargs: Dict[str, "Connectable"]):
        # Create our internal structures
        # The core namespace of Signals, other Bundles, and any other Connectables
        self._namespace: Dict[str, "Signal"] = dict()
        # Connected port references
        self._connected_ports: Set["PortRef"] = set()

        # And add each keyword-arg
        for key, val in kwargs.items():
            self.add(key, val)

    def add(self, name: str, val: BundleAttr) -> BundleAttr:
        """Add attribute `val` to our namespace."""

        if name in self._namespace:
            raise RuntimeError(f"Duplicate attribute {name} in {self}")
        if not is_connectable(val):
            raise TypeError(f"Invalid Bundle attribute {val} for {self}")
        self._namespace[name] = val
        return val

    def get(self, name: str) -> Optional["Connectable"]:
        """Get attribute `name`. Returns `None` if not present.
        Note unlike Python built-ins such as `getattr`, `get` returns solely
        from the HDL namespace-worth of attributes."""
        return self._namespace.get(name, None)


def bundlize(**kwargs) -> AnonymousBundle:
    """# Bundle-ize
    "Collect" a group of Signals and Bundle instances into an anonymous Bundle."""
    return AnonymousBundle(**kwargs)


@getattr_bundle_refs
@concatable
@sliceable
@connectable
@init
class BundleRef:
    """Reference into a Bundle Instance"""

    _specialcases: ClassVar[List[str]] = [
        "parent",
        "attrname",
        "path",
        "root",
        "refs_to_me",
        "resolved",
    ]

    def __init__(
        self,
        parent: Union["BundleInstance", "BundleRef"],  # Parent Bundle
        attrname: str,  # Attribute name
    ):
        self.parent = parent
        self.attrname = attrname

        self.resolved: Union[None, "Signal", "BundleInstance"] = None
        # References handed out to our children
        self.refs_to_me: Dict[str, "BundleRef"] = dict()
        self._width: Optional[int] = None  # FIXME: remove?
        self._slices: Set["Slice"] = set()
        self._concats: Set["Concat"] = set()
        self._connected_ports: Set["PortRef"] = set()

        self._elaborated = False
        self._initialized = True

    def __eq__(self, other) -> bool:
        """Port-reference equality requires *identity* between parents
        (and of course equality of attribute-name)."""
        return self.inst is other.inst and self.attrname == other.attrname

    def __hash__(self):
        """Hash references as the tuple of their instance-address and name"""
        return hash((id(self.inst), self.attrname))

    def path(self) -> List[str]:
        """Get the path to this potentially nested reference."""
        if isinstance(self.parent, BundleRef):
            return self.parent.path() + [self.attrname]
        if isinstance(self.parent, BundleInstance):
            return [self.attrname]
        raise TypeError

    def root(self) -> "BundleInstance":
        """Get the root `BundleInstance` of this potentially nested reference."""
        if isinstance(self.parent, BundleRef):
            return self.parent.root()
        if isinstance(self.parent, BundleInstance):
            return self.parent
        raise TypeError

    def __repr__(self):
        return f"{self.__class__.__name__}(root={self.root()} path={self.path()})"


def _bundle_ref(self: Union[BundleRef, BundleInstance], key: str) -> BundleRef:
    """Return a reference to name `key`, creating it if necessary."""

    # Check in our existing references
    bundle_refs = self.__getattribute__("refs_to_me")
    if key in bundle_refs:
        return bundle_refs[key]

    # New reference; create, add, and return it
    bundle_ref = BundleRef(parent=self, attrname=key)
    bundle_refs[key] = bundle_ref
    return bundle_ref
