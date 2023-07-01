""" 
# `hdl21.Bundle` and Related Classes 

Structured connection objects, instances thereof, and associated utilities.
"""

# Std-Lib Imports
import warnings
from copy import copy
from enum import Enum, EnumMeta
from typing import Optional, Union, Any, Dict, Set, List, ClassVar

# Local Imports
from . import attrmagic
from .role import Role, RoleSet
from .connect import connectable, is_connectable
from .sliceable import sliceable
from .concat import concatable
from .signal import Signal
from .visibility import Visibility
from .props import Properties


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
@attrmagic.only_set_known_attrs
@attrmagic.init
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
        "props",
        "refs_to_me",
    ]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        of: "Bundle",
        port: bool = False,
        flipped: bool = False,
        role: Union[Role, Enum, None] = None,
        src: Union[Role, Enum, None] = None,
        dest: Union[Role, Enum, None] = None,
        desc: Optional[str] = None,
    ):
        self.name = name
        self.of = of
        self.port = port  # FIXME: make this a `Visibility`
        self.flipped = flipped
        self.role = role
        self.src = src
        self.dest = dest
        self.desc = desc
        # References handed out to our children
        self.refs_to_me: Dict[str, "BundleRef"] = dict()
        self.props: Properties = Properties()
        # Connected port references
        self._connected_ports: Set["PortRef"] = set()
        self._parent_module: Optional["Module"] = None
        self._elaborated = False
        self._initialized = True

    @property
    def _resolved(self) -> "Bundle":
        return self.of

    """ Special Methods """

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name} of={self.of})"

    def __rmul__(self, num: int) -> List["Self"]:
        """# Right multiplication. Creates `num` copies of ourselves."""
        if not isinstance(num, int):
            return NotImplemented
        return [copy(self) for _ in range(num)]


# Type-alias for HDL objects storable as `Module` attributes
BundleAttr = Union[Signal, BundleInstance]


def is_bundle_attr(val: Any) -> bool:
    """Boolean indication of whether `val` is a valid `hdl21.Bundle` attribute."""
    return isinstance(val, BundleAttr.__args__)


def assert_bundle_attr(b: "Bundle", val: Any) -> None:
    """Raise a TypeError if `val` is not a valid attribute."""
    if not is_bundle_attr(val):
        msg = f"Invalid attribute {val} added to {b}"
        raise TypeError(msg)


_banned = ["signals", "bundles", "namespace"]


@attrmagic.init
class Bundle:
    """
    # hdl21 Bundle

    Bundles are structured hierarchical connection objects which include Signals and other Bundles.
    """

    def __init__(self, *, name: Optional[str] = None):
        self.name: Optional[str] = name
        self.roles: Optional[RoleSet] = None
        self.signals: Dict[str, "Signal"] = dict()
        self.bundles: Dict[str, "BundleInstance"] = dict()
        self.namespace: Dict[str, "BundleAttr"] = dict()  # Combination of all these
        self.props: Properties = Properties()
        self._elaborated = (
            False  # FIXME: unify whether these are boolean, or Optional objects
        )
        self._initialized = True  # Done running __init__, enable some magic

    """
    The public `Bundle` API. Just `add` and `get`. 
    To keep the space of valid names for post-fix dot access as large as possible, 
    the `Bundle` class namespace is kept *as small* as possible. 
    """

    def add(self, val: BundleAttr, *, name: Optional[str] = None) -> BundleAttr:
        """Add a Bundle attribute.

        `Bundle.add` allows for programmatic insertion of attributes whose names are not legal Python identifiers,
        such as keywords ('in', 'from') and those including invalid characters.

        The added object `val` is also provided as the return value, enabling chaining-style usages such as
        ```python
        instance.inp = MyBundle.add(h.Input(name="in", width=5))
        ```
        and similar.

        Attribute naming comes from one of either:
        * `val`'s `name` attribute, if it has one, or
        * The optional `name` argument.
        Only one of the two name-sources is allowed per call.
        """

        # Check it's a valid attribute-type
        assert_bundle_attr(self, val)

        # Now sort out naming. We get two name-sources:
        # (a) the function-argument `name` and (b) the value's `name` attribute.
        # One or the other (and not both) must be set.
        if name is None and val.name is None:  # Neither set, fail.
            msg = f"Anonymous attribute {val} cannot be added to Bundle {self.name}"
            raise RuntimeError(msg)
        if name is not None and val.name is not None:  # Both set, fail.
            msg = f"{val} with conflicting names {name} and {val.name} cannot be added to Bundle {self.name}"
            raise RuntimeError(msg)
        if name is not None:  # One or the other set - great.
            val.name = name

        # Now `val.name` is set appropriately.
        # Add it to our type-based containers, and return it.
        return _add(bundle=self, val=val)

    def get(self, name: str) -> Optional[BundleAttr]:
        """Get attribute `name`. Returns `None` if not present.
        Note unlike Python built-ins such as `getattr`, `get` returns solely
        from the HDL namespace-worth of `BundleAttr`s."""
        ns = self.__getattribute__("namespace")
        return ns.get(name, None)

    @property
    def Roles(self):
        """# Roles Accessor Property"""
        # Roles often look like a class, so they have a class-style name-accessor
        return self.roles

    """
    Special Methods
    """

    def __setattr__(self, key: str, val: Any) -> None:
        """Set-attribute over-ride, organizing into type-based containers"""

        if key.startswith("_") or not getattr(self, "_initialized", False):
            # Bootstrapping phase. Pass along to "regular" setattr.
            return super().__setattr__(key, val)

        if key in _banned:
            msg = f"Error attempting to over-write protected attribute {key} of Module {self}"
            raise RuntimeError(msg)
        # Special case(s)
        if key == "name":
            return super().__setattr__(key, val)
        if key == "roles":
            if isinstance(val, EnumMeta):
                # FIXME: deprecation warning and inline conversion here for now!
                msg = f"Bundle roles should be a `RoleSet`. Use `RoleSet.from_enum` to convert an `Enum` class!"
                warnings.warn(DeprecationWarning(msg))
                val = RoleSet.from_enum(val)
            if not isinstance(val, RoleSet):
                raise TypeError(f"Bundle roles must be an `RoleSet`, not {val}")

            return super().__setattr__(key, val)

        # Check it's a valid attribute-type
        assert_bundle_attr(self, val)

        # Checks out! Name `val` and add it to our type-based containers.
        val.name = key
        _add(bundle=self, val=val)
        return None

    def __getattr__(self, key):
        ns = self.__getattribute__("namespace")
        if key in ns:
            return ns[key]
        return object.__getattribute__(self, key)

    def __call__(self, **kwargs):
        """Calls to Bundles return Bundle Instances"""
        return BundleInstance(of=self, **kwargs)

    def __init_subclass__(cls, *_, **__):
        """Sub-Classing Disable-ization"""
        msg = f"Error attempting to create {cls.__name__}. Sub-Typing hdl21.Bundle is not supported."
        raise RuntimeError(msg)

    def __repr__(self) -> str:
        if self.name:
            return f"Bundle(name={self.name})"
        return f"Bundle(_anon_)"


def _add(bundle: Bundle, val: BundleAttr) -> BundleAttr:
    """Internal `Module.add` and `Module.__setattr__` implementation.
    Primarily sort `val` into one of our type-based containers.
    Layers above `_add` must ensure that `val` has its `name` attribute before calling this method."""

    if bundle._elaborated:  ## FIXME: is not None:
        raise RuntimeError(f"Cannot add {val} to {bundle} after elaboration.")

    # Sort out which of our type-based containers to add `val` to.
    if isinstance(val, Signal):
        type_ctr = bundle.signals
    elif isinstance(val, BundleInstance):
        type_ctr = bundle.bundles
    elif isinstance(val, Role):
        type_ctr = bundle.roles.inner
    else:
        # The next line *should* never be reached, as outer layers should have checked `_is_bundle_attr`.
        # Nonetheless gotta raise an error if we get here, somehow.
        msg = f"Invalid Bundle attribute {val} for {bundle}"
        raise TypeError(msg)

    # Add it to the bundle namespace, and the type-specific container
    type_ctr[val.name] = val
    bundle.namespace[val.name] = val

    # Give it a reference to us
    val._parent_bundle = bundle

    # And return our newly-added attribute
    return val


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
    # Collect a list of all declared `Role`s
    roles_dict: Dict[str, Role] = dict()

    # Take a lap through the class dictionary, type-check everything and assign relevant attributes to the bundle
    for key, val in cls.__dict__.items():
        if key in protected_names:
            raise RuntimeError(f"Invalid field name {key} in bundle {cls}")
        elif key == "roles" or key == "Roles":
            # Special-case the upper-cased `Roles`, as it'll often be a class-def
            setattr(bundle, "roles", val)
        elif isinstance(val, Role):
            roles_dict[key] = val
        elif is_bundle_attr(val):
            setattr(bundle, key, val)
        else:  # Add to the forget-list
            forgetme.append(val)

    # Sort out the role definitions.
    # This can come either from a single `roles`/`Roles` attribute, or from a list of `Role`s, but not both.
    if roles_dict:
        if bundle.roles is not None:
            msg = f"Error attempting to define roles for {bundle} when it already has roles {bundle.roles}"
            raise RuntimeError(msg)
        # Defined via list. Convert to a `RoleSet`.
        bundle.roles = RoleSet.from_dict(roles_dict)

    # And return the bundle
    return bundle


@attrmagic.no_setattr
@attrmagic.init
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

        self._initialized = True

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
@attrmagic.only_set_known_attrs
@attrmagic.init
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
        raise TypeError(f"Invalid parent {self.parent} for {self}")

    def root(self) -> "BundleInstance":
        """Get the root `BundleInstance` of this potentially nested reference."""
        if isinstance(self.parent, BundleRef):
            return self.parent.root()
        if isinstance(self.parent, BundleInstance):
            return self.parent
        raise TypeError(f"Invalid parent {self.parent} for {self}")

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


def flippable(b: Bundle) -> bool:
    """
    # Boolean indication of whether a Bundle is flippable.
    Requires that all Signals in the Bundle,
    and all Signals in all its sub-bundles, have port-visibility.
    """
    return all([s.vis == Visibility.PORT for s in b.signals.values()]) and all(
        [flippable(bi.of) for bi in b.bundles.values()]
    )


def flipped(bi: BundleInstance) -> BundleInstance:
    """# Create a flipped copy of a BundleInstance"""
    cp = copy(bi)
    cp.flipped = not cp.flipped
    return cp


__all__ = [
    "Bundle",
    "bundle",
    "BundleInstance",
    "AnonymousBundle",
    "bundlize",
    "flipped",
    "BundleRef",  # FIXME: remove
]
