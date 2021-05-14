""" 
# Hdl21 Hierarchical Instances 

Create instances of Modules, Generators, and Primitives in a hierarchy
"""

from pydantic.dataclasses import dataclass
from typing import Optional, Union

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

    _specialcases = ["name", "of", "conns", "portrefs", "_elaborated", "_initialized"]

    def __init__(
        self,
        of: Union["Module", "Generator", "GeneratorCall"],
        params: Optional[object] = None,
    ):
        from .generator import Generator, GeneratorCall
        from .module import Module
        from .interface import InterfaceInstance

        if isinstance(of, Generator):
            of = of(params)
        elif isinstance(of, (Module, GeneratorCall)) and params is not None:
            raise RuntimeError(
                f"Invalid instance with parameters {params}. Instance parameters can be used with *generator* functions. "
            )
        self.of = of
        self.params = params
        self.conns = dict()
        self.portrefs = dict()
        self._elaborated = False
        self._initialized = True

    @property
    def module(self) -> Optional["Module"]:
        from .module import Module
        from .generator import GeneratorCall

        if isinstance(self.of, Module):
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
        *,
        params: Optional[object] = None,
    ):
        from .generator import Generator, GeneratorCall
        from .module import Module

        if isinstance(of, Generator):
            of = of(params)
        elif isinstance(of, (Module, GeneratorCall)) and params is not None:
            raise RuntimeError(
                f"Invalid instance with parameters {params}. Instance parameters can be used with *generator* functions. "
            )
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

