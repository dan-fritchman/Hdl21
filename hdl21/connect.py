"""
# hdl21 Connection Helpers 

Decorators which add a number of connection-related facilities onto classes to which they are applied. 
"""
from typing import Any, Union


def connectable(cls: type) -> type:
    """ Decorator for connectable types """
    cls.__connects__ = True
    return cls


def is_connectable(obj: Any) -> bool:
    """ Boolean indication of connect-ability """
    return getattr(obj, "__connects__", False)


def connects(cls: type) -> type:
    """ Decorator to add 'connect by call' and 'connect by setattr' semantics. 
    Applied to hdl21 internal types such as `Instance`, `InstArray` and `InterfaceInstance`. 
    
    `connects` classes have a few more subtle requirements, including that they 
    indicate when their constructors complete via an `_initialized` field, 
    include a `conns` connections-dict, and a `portrefs` dictionary of past port-references. """

    # First check and fail if any of the methods to be defined here are already defined elsewhere
    defined_here = ["__call__", "__setattr__", "__getattr__", "connect"]
    for key in defined_here:
        if key in cls.__dict__:
            raise RuntimeError(
                f"Invalid modification of {cls} with `@hdl21.connects`: {key} is already defined, and will not be over-written."
            )

    def __call__(self, **kwargs) -> "Self":
        """ Connect-by-call """
        for key, val in kwargs.items():
            self.connect(key, val)
        # Don't forget to retain ourselves at the call-site!
        return self

    def __setattr__(self, key: str, val: Any) -> None:
        """ Connect-by-setattr """
        if not getattr(self, "_initialized", False) or key.startswith("_"):
            # Bootstrapping phase: do regular setattrs to get started
            return object.__setattr__(self, key, val)
        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__setattr__(self, key, val)
        self.connect(key, val)

    def connect(self, portname: str, signal: Union["Signal", "PortRef"]) -> "Self":
        """ Connect Signal `signal` to port (name) `portname`. 
        Called by both by-call and by-assignment convenience methods, and usable directly. 
        Direct calls to `connect` will generally be required for ports with otherwise illegal names, 
        e.g. Python language keywords (`in`, `from`, etc.), 
        or Hdl21 internal "keywords" (`name`, `ports`, `signals`, etc.). 
        Returns `self` to aid in method-chaining use-cases. """
        if not is_connectable(signal):
            raise TypeError(f"{self} attempting to connect non-connectable {signal}")
        self.conns[portname] = signal
        return self

    def __getattr__(self, key: str) -> Any:
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

        # Return a `PortRef`, creating one if necessary
        return self.port_ref(key)

    def port_ref(self, key: str) -> "PortRef":
        """ Return a port-reference to name `key`, creating it if necessary. """
        from .instance import PortRef

        # Check in our existing port-references
        port_refs = self.__getattribute__("portrefs")
        if key in port_refs:
            return port_refs[key]

        # New reference; create, add, and return it
        port_ref = PortRef(inst=self, portname=key)
        port_refs[key] = port_ref
        return port_ref

    # Attach all of these to the class
    cls.__call__ = __call__
    cls.__setattr__ = __setattr__
    cls.__getattr__ = __getattr__
    cls.connect = connect
    cls.port_ref = port_ref

    # And don't forget to return it!
    return cls
