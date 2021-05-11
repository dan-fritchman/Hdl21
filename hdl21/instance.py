""" 
# Hdl21 Hierarchical Instances 

Create instances of Modules, Generators, and Primitives in a hierarchy
"""

from pydantic.dataclasses import dataclass
from typing import Optional, Union

from .module import Module


@dataclass
class PortRef:
    """ Port Reference to an Instance or Array """

    inst: Union["Instance", "InstArray"]
    portname: str


PortRef.__pydantic_model__.Config.arbitrary_types_allowed = True


def connects(cls: type) -> type:
    """ Decorator to add 'connect by call' and 'connect by setattr' semantics. """
    from .signal import Signal

    def __call__(self, **kwargs):
        """ Connect-by-call """

        for k, v in kwargs.items():
            if not isinstance(v, (Signal, PortRef)):
                raise TypeError
            self.conns[k] = v
        # Don't forget to retain ourselves at the call-site!
        return self

    def __setattr__(self, key: str, val: object):
        """ Connect-by-setattr """
        if not getattr(self, "_initialized", False) or key.startswith("_"):
            # Bootstrapping phase: do regular setattrs to get started
            return object.__setattr__(self, key, val)
        if key == "name":  # Special case(s)
            return object.__setattr__(self, key, val)

        if not isinstance(val, (Signal, PortRef)):
            raise TypeError
        self.conns[key] = val

    def __getattr__(self, key: str):
        """ Port access by getattr """
        if not self.__getattribute__("_initialized") or key.startswith("_"):
            # Bootstrapping phase: do regular getattrs to get started
            return object.__getattr__(self, key)
        if key == "name":  # Special case(s)
            return object.__getattr__(self, key)
        # Return anything already connected to us by name `key`
        conns = self.__getattribute__("conns")
        if key in conns.keys():
            return conns[key]

        # If we have a concrete Module, check whether it has this as a port, and only return it if so
        # (If it's a generator, in contrast, we don't necessarily know the ports yet.)
        if isinstance(self.of, Module) and key not in self.of.ports:
            raise RuntimeError(f"Invalid port {key} accessed on Module {self.of}")
        # Check in our existing port-references
        port_refs = self.__getattribute__("_port_refs")
        if key in port_refs.keys():
            return port_refs[key]
        # New reference; create, add, and return it
        port_ref = PortRef(inst=self, portname=key)
        port_refs[key] = port_ref
        return port_ref

    cls.__call__ = __call__
    cls.__setattr__ = __setattr__
    cls.__getattr__ = __getattr__
    cls.__connects__ = True
    return cls


@connects
class Instance:
    """ Hierarchical Instance of another Module or Generator """

    def __init__(
        self,
        of: Union["Module", "Generator", "GeneratorCall"],
        params: Optional[object] = None,
    ):
        from .generator import Generator, GeneratorCall

        if isinstance(of, Generator):
            of = of(params)
        elif isinstance(of, (Module, GeneratorCall)) and params is not None:
            raise RuntimeError(
                f"Invalid instance with parameters {params}. Instance parameters can be used with *generator* functions. "
            )
        self.of = of
        self.params = params
        self.conns = dict()
        self._port_refs = dict()
        self._initialized = True


@connects
class InstArray:
    """ Array of Instances """

    def __init__(
        self,
        of: Union["Module", "Generator", "GeneratorCall"],
        n: int,
        *,
        params: Optional[object] = None,
    ):
        from .generator import Generator, GeneratorCall

        if isinstance(of, Generator):
            of = of(params)
        elif isinstance(of, (Module, GeneratorCall)) and params is not None:
            raise RuntimeError(
                f"Invalid instance with parameters {params}. Instance parameters can be used with *generator* functions. "
            )
        self.of = of
        self.params = params
        self.conns = dict()
        self._port_refs = dict()

        # So far, this is the only difference from `Instance`. Better sharing likely awaits.
        self.n = n
        self._initialized = True


PortRef.__pydantic_model__.update_forward_refs()

