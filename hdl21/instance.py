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
    """ Port Reference to an Instance or Array """

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
class Instance:
    """ Hierarchical Instance of another Module or Generator """

    _specialcases = [
        "name",
        "of",
        "conns",
        "portrefs",
        "_resolved",
        "_elaborated",
        "_initialized",
    ]

    def __init__(
        self,
        of: Union["Module", "Generator", "GeneratorCall", "PrimitiveCall"],
        params: Optional[object] = None,
        *,
        name: Optional[str] = None,
    ):
        from .generator import Generator, GeneratorCall
        from .module import Module
        from .primitives import PrimitiveCall

        if isinstance(of, Generator):
            of = of(params)
        elif (
            isinstance(of, (Module, GeneratorCall, PrimitiveCall))
            and params is not None
        ):
            raise RuntimeError(
                f"Invalid instance with parameters {params}. Instance parameters can be used with *generator* functions. "
            )
        self.name = name
        self.of = of
        self.params = params
        self.conns = dict()
        self.portrefs = dict()
        self._elaborated = False
        self._initialized = True

    def __repr__(self):
        return f"Instance(name={self.name} of={self.of})"

    @property
    def _resolved(self) -> Optional[Union["Module", "PrimitiveCall"]]:
        """ Property to retrieve the Instance's resolved Module, if complete. 
        Returns `None` if unresolved. """
        from .module import Module
        from .generator import GeneratorCall
        from .primitives import PrimitiveCall

        if isinstance(self.of, (Module, PrimitiveCall)):
            return self.of
        if isinstance(self.of, GeneratorCall):
            return self.of.result
        return None


@connects
class InstArray:
    """ Array of Instances """

    _specialcases = ["name", "of", "conns", "portrefs", "_elaborated", "_initialized"]

    def __init__(
        self,
        of: Union["Module", "Generator", "GeneratorCall"],
        n: int,
        params: Optional[object] = None,
        *,
        name: Optional[str] = None,
    ):
        from .generator import Generator, GeneratorCall
        from .module import Module

        if isinstance(of, Generator):
            of = of(params)
        elif isinstance(of, (Module, GeneratorCall)) and params is not None:
            raise RuntimeError(
                f"Invalid instance with parameters {params}. Instance parameters can be used with *generator* functions. "
            )
        self.name = name
        self.of = of
        self.params = params
        self.conns = dict()
        self.portrefs = dict()

        # So far, this is the only difference from `Instance`. Better sharing likely awaits.
        self.n = n
        self._elaborated = False
        self._initialized = True


# Get the runtime type-checking to understand the types forward-referenced and then defined here
from .interface import InterfaceInstance

PortRef.__pydantic_model__.Config.arbitrary_types_allowed = True
PortRef.__pydantic_model__.update_forward_refs()


def calls_instantiate(cls: type) -> type:
    """ Decorator which adds 'calls produce `hdl21.Instances` functionality. """

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
