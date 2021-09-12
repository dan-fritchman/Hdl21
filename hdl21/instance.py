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


class _Instance:
    """ Shared base class for Instance-like types (Instance, InstArray) """

    _specialcases = [
        "name",
        "of",
        "conns",
        "portrefs",
        "connect",
        "_resolved",
        "_elaborated",
        "_initialized",
    ]

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

    ...


@connects
class InstArray(_Instance):
    """ Array of `n` Instances """

    _specialcases = [
        "name",
        "of",
        "conns",
        "portrefs",
        "connect",
        "_elaborated",
        "_initialized",
    ]

    def __init__(
        self, of: "Instantiable", n: int, name: Optional[str] = None,
    ):
        self.n = n
        super().__init__(of=of, name=name)


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
        raise RuntimeError(
            f"Hdl21 Internal Error: Invalid conflict between `calls_instantiate` decorator and explicit `__call__` method on {cls}"
        )
    cls.__call__ = __call__
    return cls
