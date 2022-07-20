""" 
# Hdl21 Hierarchical Instances 

Create instances of Modules, Generators, and Primitives in a hierarchy
"""

# Std-Lib Imports
from typing import Optional, Any, Dict
from textwrap import dedent

# Local imports
from .source_info import source_info, SourceInfo
from .attrmagic import init
from .connect import (
    call_and_setattr_connects,
    getattr_port_refs,
)


@call_and_setattr_connects
@getattr_port_refs
@init
class _Instance:
    """Shared base class for Instance-like types (Instance, InstArray)"""

    def __init__(
        self,
        of: "Instantiable",
        *,
        name: Optional[str] = None,
    ):
        from .instantiable import is_instantiable

        if not is_instantiable(of):
            raise RuntimeError(f"Invalid Instance of {of}")

        self.name: Optional[str] = name
        self.of: "Instantiable" = of
        self.conns: Dict[str, "Connectable"] = dict()
        self.portrefs: Dict[str, "PortRef"] = dict()
        self._parent_module = None  # Instantiating module
        self._elaborated = False
        self._source_info: Optional[SourceInfo] = source_info([__file__])

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name} of={self.of})"

    @property
    def _resolved(
        self,
    ) -> Optional["Instantiable"]:
        """Property to retrieve the Instance's resolved Module, if complete.
        Returns `None` if unresolved."""
        from .generator import GeneratorCall

        if isinstance(self.of, GeneratorCall):
            return self.of.result
        return self.of


def _to_array(inst: "Instance", num: int) -> "InstArray":
    """Create an Instance Array from an Instance"""
    # Several contraints asserted here which may eventually be relaxed.
    # * No port-references (yet)
    # * Not a member of a module (yet)
    if len(inst.portrefs) > 0:
        msg = f"Cannot convert Instance {inst} with outstanding port-references {inst.portrefs} to Array"
        raise RuntimeError(msg)
    if inst._parent_module is not None:
        msg = f"Cannot convert Instance {inst} already inserted in Module {inst._parent_module} to Array"
        raise RuntimeError(msg)

    # Checks out. Create the array.
    return InstArray(of=inst.of, n=num, name=inst.name)(**inst.conns)


def _mult(inst: "Instance", other: int) -> "InstArray":
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
        "portref",
        "portrefs",
        "connect",
        "disconnect",
        "replace",
    ]

    def __init__(self, *_, **__):
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
        "portref",
        "portrefs",
        "connect",
        "disconnect",
        "replace",
    ]

    def __init__(self, *_, **__):
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


class InstArray(_Instance):
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
        self,
        of: "Instantiable",
        n: int,
        name: Optional[str] = None,
    ):
        super().__init__(of=of, name=name)
        self.n = n
        self._initialized = True

    def __getitem__(self, idx: int):
        return RuntimeError(f"Illegal indexing into Array {self}")

    def __setitem__(self, _idx: Any, _val: Any):
        return RuntimeError(f"Illegal indexing into Array {self}")


def calls_instantiate(cls: type) -> type:
    """Decorator which adds 'calls produce `hdl21.Instance`s' functionality."""

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


__all__ = [
    "Instance",
    "InstArray",
    "InstanceBundle",
    "InstanceBundleType",
    "calls_instantiate",
]
