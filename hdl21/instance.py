import builtins
import inspect

from textwrap import dedent
from pydantic.dataclasses import dataclass
from typing import ClassVar, Optional, Union, Callable, Any

from .module import Module
from .generator import Generator


def connects(cls: type) -> type:
    """ Decorator to add 'connect by call' and 'connect by setattr' semantics. """

    def __call__(self, **kwargs):
        """ Connect-by-call """
        from .signal import Signal

        for k, v in kwargs.items():
            if not isinstance(v, Signal):
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

        from .signal import Signal

        if not isinstance(val, Signal):
            raise TypeError
        self.conns[key] = val

    def __getattr__(self, key: str):
        """ Port access by getattr """
        if not self.__getattribute__("_initialized") or key.startswith("_"):
            # Bootstrapping phase: do regular getattrs to get started
            return object.__getattr__(self, key)
        if key == "name":  # Special case(s)
            return object.__getattr__(self, key)
        conns = self.__getattribute__("conns")
        if key in conns:
            return conns[key]
        # If we have a concrete Module, check whether it has this as a port, and only return it if so
        if isinstance(self.of, Module):
            if key not in self.of.ports:
                raise RuntimeError(f"Invalid port {key} accessed on Module {self.of}")
            return self.of.ports[key]

        # FIXME: whether to support Generators.
        # This would require some paired logic ordering how they elaborate.
        # Which, we probably want, but don't have for now.
        raise RuntimeError(f"Invalid access to generator port {key} on instance {self}")
        # If this is a generator, we don't necessarily know the ports yet.
        # Create and return a port-reference, to be elaborated (maybe) post-generation
        # return PortRef(inst=self, portname=key)

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
        of: Union[Module, "Generator", "GeneratorCall"],
        params: Optional[object] = None,
    ):
        if isinstance(of, Module) and params is not None:
            raise RuntimeError(
                f"Invalid Module-instance with parameters {params}. Instance parameters can be used with *generator* functions. "
            )
        self.of = of
        self.params = params
        self.conns = dict()
        self._initialized = True


@connects
class InstArray:
    """ Array of Instances """

    def __init__(
        self,
        of: Union[Module, "Generator", "GeneratorCall"],
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
        self.n = n
        self.params = params
        self.conns = dict()
        self._initialized = True


@dataclass
class PortRef:
    """ Port Reference to an Instance or Array """

    inst: Any  # FIXME! Union[Instance, InstArray]
    portname: str
