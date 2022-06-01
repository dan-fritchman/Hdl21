""" 
# `hdl21.Bundle` and Related Classes 

Structured connection objects, instances thereof, and associated utilities.
"""

from enum import Enum, EnumMeta
from typing import Optional, Union, Any, get_args, Dict, List

# Local Imports
from .connect import connectable, track_connected_ports
from .signal import Signal


def getattr_bundle_refs(cls: type) -> type:
    """ Decorator to add the "__getattr__ generates BundleRefs" functionality to `cls`. 
    Adds the `_bundle_ref` method and `__getattr__` access to it. """

    # First check and fail if any of the methods to be defined here are already defined elsewhere
    defined_here = ["_bundle_ref", "__getattr__"]
    for key in defined_here:
        if key in cls.__dict__:
            msg = f"Invalid modification of {cls} with `@getattr_bundle_refs`: {key} is already defined."
            raise RuntimeError(msg)

    def _bundle_ref(self, key: str) -> "BundleRef":
        """ Return a reference to name `key`, creating it if necessary. """

        # Check in our existing references
        bundle_refs = self.__getattribute__("refs")
        if key in bundle_refs:
            return bundle_refs[key]

        # New reference; create, add, and return it
        bundle_ref = BundleRef(parent=self, attrname=key)
        bundle_refs[key] = bundle_ref
        return bundle_ref

    def __getattr__(self, key: str) -> Any:
        """ BundleRef access by getattr """
        if not self.__getattribute__("_initialized") or key.startswith("_"):
            # Bootstrapping phase: do regular getattrs to get started
            return object.__getattribute__(self, key)

        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__getattribute__(self, key)

        # After elaboration, the fancy BundleRef creation below goes away. Only return ready-made refs.
        if self.__getattribute__("_elaborated"):
            refs = self.__getattribute__("refs")
            if key in refs.keys():
                return refs[key]
            raise AttributeError(f"No attribute {key} for {self}")

        # Fell through all those cases. Fancy `BundleRef` generation time!
        # Return a `BundleRef`, creating one if necessary.
        return self._bundle_ref(key)

    cls._bundle_ref = _bundle_ref
    cls.__getattr__ = __getattr__
    cls.__getattr_bundle_refs__ = True

    # And don't forget to return it!
    return cls


def has_getattr_bundle_refs(obj: Any) -> bool:
    """ Boolean indication of "getattr bundle refs" functionality """
    return getattr(obj, "__getattr_bundle_refs__", False)


@getattr_bundle_refs
@track_connected_ports
@connectable
class BundleInstance:
    """ Instance of an Bundle, 
    Generally in a Module or another Bundle """

    _specialcases = [
        "name",
        "of",
        "port",
        "role",
        "src",
        "dest",
        "desc",
        "refs",
        "connected_ports",
        "_bundle_ref",
        "_elaborated",
        "_initialized",
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
        self.refs: Dict[str, "BundleRef"] = dict()
        # Connected port references
        self.connected_ports: List["BundleRef"] = []
        self._elaborated = False
        self._initialized = True

    @property
    def _resolved(self) -> "Bundle":
        return self.of


# Type-alias for HDL objects storable as `Module` attributes
BundleAttr = Union[Signal, BundleInstance]


def is_bundle_attr(val: Any) -> bool:
    """ Boolean indication of whether `val` is a valid `hdl21.Bundle` attribute. """
    return isinstance(val, get_args(BundleAttr))


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
        """ Set-attribute over-ride, organizing into type-based containers """
        from .signal import Signal

        if not getattr(self, "_initialized", False) or key.startswith("_"):
            return super().__setattr__(key, val)

        # Protected attrs - the internal dicts
        banned = ["signals", "bundles", "namespace"]
        if key in banned:
            raise RuntimeError(
                f"Error attempting to over-write protected attribute {key} of Bundle {self}"
            )
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
        """ Calls to Bundles return Bundle Instances """
        return BundleInstance(of=self, **kwargs)

    def __init_subclass__(cls, *_args, **_kwargs):
        """ Sub-Classing Disable-ization """
        msg = f"Error attempting to create {cls.__name__}. Sub-Typing hdl21.Bundle is not supported."
        raise RuntimeError(msg)

    def add(self, val: BundleAttr, *, name: Optional[str] = None) -> BundleAttr:
        raise NotImplementedError

    def get(self, name: str) -> Optional[BundleAttr]:
        """ Get module-attribute `name`. Returns `None` if not present. 
        Note unlike Python built-ins such as `getattr`, `get` returns solely 
        from the HDL namespace-worth of `BundleAttr`s. """
        ns = self.__getattribute__("namespace")
        return ns.get(name, None)

    @property
    def Roles(self):
        """ Roles-Enumeration Accessor Property """
        # Roles often look like a class, so they have a class-style name-accessor
        return self.roles


def bundle(cls: type) -> Bundle:
    """ # Bundle Definition Decorator 
    
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

    """
    if cls.__bases__ != (object,):
        raise RuntimeError(f"Invalid @hdl21.bundle inheriting from {cls.__bases__}")

    # Create the Bundle object
    bundle = Bundle(name=cls.__name__)

    protected_names = ["signals", "bundles"]
    dunders = dict()
    unders = dict()

    # Take a lap through the class dictionary, type-check everything and assign relevant attributes to the bundle
    for key, val in cls.__dict__.items():
        if key in protected_names:
            raise RuntimeError(f"Invalid field name {key} in bundle {cls}")
        elif key.startswith("__"):
            dunders[key] = val
        elif key.startswith("_"):
            unders[key] = val
        elif key == "Roles":
            # Special-case the upper-cased `Roles`, as it'll often be a class-def
            setattr(bundle, "roles", val)
        else:
            setattr(bundle, key, val)
    # And return the bundle
    return bundle


@track_connected_ports
@connectable
class AnonymousBundle:
    """ # Anonymous Connection Bundle 
    Commonly used for "collecting" Signals into `h.Bundle`s, 
    or for re-jiggering connections between `h.Bundle`s. """

    def __init__(self, **kwargs: Dict[str, "Connectable"]):
        # Create our internal structures
        self.signals: Dict[str, "Signal"] = dict()
        self.bundles: Dict[str, "BundleInstance"] = dict()
        self.anons: Dict[str, "AnonymousBundle"] = dict()
        self.refs: Dict[str, "BundleRef"] = dict()
        # Connected port references
        self.connected_ports: List["BundleRef"] = []

        # And add each keyword-arg
        for key, val in kwargs.items():
            self.add(key, val)

    def add(self, name: str, val: BundleAttr) -> BundleAttr:
        """ Add attribute `val`. """

        if isinstance(val, Signal):
            self.signals[name] = val
        elif isinstance(val, (BundleInstance, AnonymousBundle)):
            raise NotImplementedError(f"Nested Anonymous Bundle")
        # elif isinstance(val, BundleInstance): # FIXME: NO
        #     self.bundles[name] = val
        # elif isinstance(val, AnonymousBundle):
        #     self.anons[name] = val
        # elif isinstance(val, BundleRef): # FIXME: whether to enable these. Currently not supported.
        #     self.portrefs[name] = val
        else:
            raise TypeError
        return val


@track_connected_ports
@connectable
class BundleRef:
    """ Reference into a Bundle Instance """

    _specialcases = [
        "parent",
        "refs",
        "connected_ports",
        "_bundle_ref",
        "_module",
        "_resolved",
        "_elaborated",
        "_initialized",
    ]

    def __init__(
        self, parent: Union["BundleInstance", "BundleRef"], attrname: str,
    ):
        self.parent = parent
        self.attrname = attrname
        self.refs: Dict[str, "BundleRef"] = dict()
        # Connected port references
        self.connected_ports: List["BundleRef"] = []
        self._elaborated = False
        self._initialized = True

    def __eq__(self, other) -> bool:
        """ Port-reference equality requires *identity* between parents 
        (and of course equality of attribute-name). """
        return self.inst is other.inst and self.attrname == other.attrname

    def __hash__(self):
        """ Hash references as the tuple of their instance-address and name """
        return hash((id(self.inst), self.attrname))


def resolve_bundle_ref(bref: BundleRef) -> Union[Signal, BundleInstance]:
    """ Resolve a bundle-reference to either a Signal or sub-Bundle Instance. """

    if isinstance(bref.parent, BundleInstance):
        # Parent is a BundleInstance. Get the attribute from its namespace.
        return bref.parent.of.get(bref.attrname)

    if isinstance(bref.parent, BundleRef):
        # Nested reference. Recursively resolve the parent.
        resolved_parent = resolve_bundle_ref(bref.parent)
        return resolved_parent.of.get(bref.attrname)

    raise TypeError(f"BundleRef parent for {bref}")
