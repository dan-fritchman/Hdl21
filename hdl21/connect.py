"""
# hdl21 Connection Helpers 

Decorators which add a number of connection-related facilities onto classes to which they are applied. 
"""
from typing import Any


def connectable(cls: type) -> type:
    """ Decorator for connectable types """
    cls.__connects__ = True
    return cls


def is_connectable(obj: Any) -> bool:
    """ Boolean indication of connect-ability """
    return getattr(obj, "__connects__", False)


def connects(cls: type) -> type:
    """ Decorator to add 'connect by call' and 'connect by setattr' semantics. 
    
    `connects` classes have a few more subtle requirements, including that they 
    indicate when their constructors complete via an `_initialized` field, 
    include a `conns` connections-dict, and a `portrefs` dictionary of past port-references. """

    def __call__(self, **kwargs):
        """ Connect-by-call """
        for k, v in kwargs.items():
            if not is_connectable(v):
                raise TypeError(f"{self} attempting to connect non-connectable {v}")
            self.conns[k] = v
        # Don't forget to retain ourselves at the call-site!
        return self

    def __setattr__(self, key: str, val: Any):
        """ Connect-by-setattr """
        if not getattr(self, "_initialized", False) or key.startswith("_"):
            # Bootstrapping phase: do regular setattrs to get started
            return object.__setattr__(self, key, val)
        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__setattr__(self, key, val)
        if not is_connectable(val):
            raise TypeError(f"{self} attempting to connect non-connectable {val}")
        self.conns[key] = val

    def __getattr__(self, key: str):
        """ Port access by getattr """
        if not self.__getattribute__("_initialized") or key.startswith("_"):
            # Bootstrapping phase: do regular getattrs to get started
            return object.__getattribute__(self, key)
        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__getattribute__(self, key)

        # After elaboration, the fancy PortRef creation below goes away. Only return ready-made connections.
        if self.__getattribute__("_elaborated"):
            conns = self.__getattribute__("conns")
            if key in conns.keys():
                return conns[key]
            raise AttributeError(f"No attribute {key} for {self}")

        from .instance import PortRef
        from .module import Module

        # If we have a concrete Module, check whether it has this as a port, and only return it if so
        # (If it's a generator, in contrast, we don't necessarily know the ports yet.)
        # FIXME: whether to run this check here, and whether to include interface-ports
        # if isinstance(self.of, Module) and key not in self.of.ports:
        #     raise RuntimeError(f"Invalid port {key} accessed on Module {self.of}")

        # Check in our existing port-references
        port_refs = self.__getattribute__("portrefs")
        if key in port_refs.keys():
            return port_refs[key]

        # New reference; create, add, and return it
        port_ref = PortRef(inst=self, portname=key)
        port_refs[key] = port_ref
        return port_ref

    cls.__call__ = __call__
    cls.__setattr__ = __setattr__
    cls.__getattr__ = __getattr__
    return cls
