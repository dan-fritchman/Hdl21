""" 
# Hdl21 Hierarchical Instances 

Create instances of Modules, Generators, and Primitives in a hierarchy
"""

from pydantic.dataclasses import dataclass
from typing import Optional, Union

# Local imports
from .connect import connectable, connects


@connectable
@dataclass
class PortRef:
    """ Port Reference to an Instance """

    inst: Union["Instance", "InstArray", "InterfaceInstance"]
    portname: str

    def __eq__(self, other) -> bool:
        """ Port-reference equality requires *identity* between instances 
        (and of course equality of port-name). """
        return self.inst is other.inst and self.portname == other.portname

    def __hash__(self):
        """ Hash references as the tuple of their instance-address and name """
        return hash((id(self.inst), self.portname))


@connects
@dataclass
class InstanceRef:
    """ Instance Reference from an Array or Group """

    parent: "InstArray"
    name: Union[int, str]

    def __eq__(self, other) -> bool:
        """ Equality requires *identity* between parents 
        (and of course equality of name). """
        return self.parent is other.parent and self.name == other.name

    def __hash__(self):
        """ Hash references as the tuple of their instance-address and name """
        return hash((id(self.parent), self.name))


class _Instance:
    """ Shared base class for Instance-like types (Instance, InstArray) """

    def __init__(
        self, of: "Instantiable", *, name: Optional[str] = None,
    ):
        from .instantiable import _is_instantiable

        if not _is_instantiable(of):
            raise RuntimeError(f"Invalid instance of {of}")

        self.name = name
        self.of = of
        self.conns = dict()
        self.portrefs = dict()
        self._parent_module = None  # Instantiating module
        self._elaborated = False
        self._initialized = True

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name} of={self.of})"

    @property
    def _resolved(self,) -> Optional["Instantiable"]:
        """ Property to retrieve the Instance's resolved Module, if complete. 
        Returns `None` if unresolved. """
        from .generator import GeneratorCall

        if isinstance(self.of, GeneratorCall):
            return self.of.result
        return self.of


@connects
class Instance(_Instance):
    """ Hierarchical Instance of another Module or Generator """

    _specialcases = [
        "name",
        "of",
        "conns",
        "portref",
        "portrefs",
        "connect",
        "_module",
        "_resolved",
        "_elaborated",
        "_initialized",
    ]

    def _mult(self, other: int) -> "InstArray":
        """ Instance by integer multiplication. 
        Creates an Instance Array of size `other`. """
        if not isinstance(other, int):
            return NotImplemented
        return self._to_array(num=other)

    __mul__ = __rmul__ = _mult  # Apply `_mult` on both left and right

    def _to_array(self, num: int) -> "InstArray":
        """ Create an Instance Array from an Instance """
        # Several contraints asserted here which may eventually be relaxed.
        # * No port-references (yet)
        # * Not a member of a module (yet)
        if len(self.portrefs) > 0:
            msg = f"Cannot convert Instance {self} with outstanding port-references {self.portrefs} to Array"
            raise RuntimeError(msg)
        if self._parent_module is not None:
            msg = f"Cannot convert Instance {self} already inserted in Module {self._parent_module} to Array"
            raise RuntimeError(msg)

        # Checks out. Create the array.
        return InstArray(of=self.of, n=num, name=self.name)(**self.conns)


@connects
class InstArray(_Instance):
    """ Array of `n` Instances """

    _specialcases = [
        "name",
        "of",
        "conns",
        "portref",
        "portrefs",
        "instrefs",
        "connect",
        "_elaborated",
        "_initialized",
        "_module",
    ]

    def __init__(
        self, of: "Instantiable", n: int, name: Optional[str] = None,
    ):
        self.instrefs = dict()
        self.n = n
        super().__init__(of=of, name=name)

    def __getitem__(self, idx: int) -> InstanceRef:
        if not isinstance(idx, int):
            return RuntimeError(f"Illegal indexing into {self} with non-integer {idx}")
        raise NotImplementedError  # FIXME: coming soon!


# Get the runtime type-checking to understand the types forward-referenced and then defined here
from .interface import InterfaceInstance

PortRef.__pydantic_model__.Config.arbitrary_types_allowed = True
PortRef.__pydantic_model__.update_forward_refs()


def calls_instantiate(cls: type) -> type:
    """ Decorator which adds 'calls produce `hdl21.Instance`s' functionality. """

    def __call__(self, **kwargs) -> Instance:
        """ Calls Create `hdl21.Instances`, 
        and pass any (keyword-only) arguments to said `Instances`, 
        generally to connect-by-call. """
        return Instance(of=self)(**kwargs)

    # Check for an existing __call__ method, and if there is one, bail
    if "__call__" in cls.__dict__:
        msg = f"Hdl21 Internal Error: Invalid conflict between `calls_instantiate` decorator and explicit `__call__` method on {cls}"
        raise RuntimeError(msg)
    cls.__call__ = __call__
    return cls
