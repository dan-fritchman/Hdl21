"""
# hdl21 Connection Helpers 

Decorators which add a number of connection-related facilities onto classes to which they are applied. 
Several such decorators are defined here, and keeping them straight can be confusing. 
From the most basic to most elaborate: 

* `connectable` - think `Signal`. 
  * Indicates that a type can serve as the *value* in a connections-dict. 
  * No added functionality, just an annotation, checked by other methods here. 
* `track_connected_ports`
  * A `connectable` type which also tracks `PortRef`s it connects to. 
  * Again, think `Signal` 
* `getattr_port_refs`
  * Adds "generate `PortRef`s via getattr" functionality. 
* `call_and_setattr_connects` - think `Instance`. 
  * The most elaborate of the bunch. 
  * For types with a connections-dict. 
  * Adds "connect by call" and "connect by setattr" functionality. 
"""

from typing import Any, Union, Dict


def connectable(cls: type) -> type:
    """ Decorator for connectable types """
    cls.__connectable__ = True
    return cls


def is_connectable(obj: Any) -> bool:
    """ Boolean indication of connect-ability """
    return getattr(obj, "__connectable__", False)


Connectable = Union["Signal", "PortRef", "BundleInstance", "AnonymousBundle"]


def track_connected_ports(cls: type) -> type:
    """ Add an annotation indicating `cls` will track `connected_ports`, 
    on a `List[PortRef]` valued field by that name. """
    if not is_connectable(cls):
        raise RuntimeError(f"Must be `@connectable`")
    cls.__track_connected_ports__ = True
    return cls


def does_track_connected_ports(obj: Any) -> bool:
    """ Boolean indication of connected-port tracking """
    return getattr(obj, "__track_connected_ports__", False)


def call_and_setattr_connects(cls: type) -> type:
    """ Decorator to add 'connect by call' and 'connect by setattr' semantics. 
    Applied to hdl21 internal types such as `Instance`, `InstArray` and `BundleInstance`. 
    
    `call_and_setattr_connects` classes have a few more subtle requirements, including that they 
    indicate when their constructors complete via an `_initialized` field, 
    include a `conns` connections-dict, and a `portrefs` dictionary of past port-references. """

    if not has_getattr_port_refs(cls):
        raise RuntimeError(f"Must be `@getattr_port_refs`")

    # First check and fail if any of the methods to be defined here are already defined elsewhere
    defined_here = ["__call__", "__setattr__", "connect"]
    for key in defined_here:
        if key in cls.__dict__:
            msg = f"Invalid modification of {cls} with `@call_and_setattr_connects`: {key} is already defined."
            raise RuntimeError(msg)

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
        _ = self.connect(key, val)  # Discard the returned `self`
        return None

    def connect(self, portname: str, conn: Connectable) -> "Self":
        """ Connect `conn` to port (name) `portname`. 
        Called by both by-call and by-assignment convenience methods, and usable directly. 
        Direct calls to `connect` will generally be required for ports with otherwise illegal names, 
        e.g. Python language keywords (`in`, `from`, etc.), 
        or Hdl21 internal "keywords" (`name`, `ports`, `signals`, etc.). 
        Returns `self` to aid in method-chaining use-cases. """
        from .bundle import AnonymousBundle
        from .instance import PortRef

        if isinstance(conn, Dict):
            # Special-case dictionaries of connectables into Anon Bundles
            conn = AnonymousBundle(**conn)
        if not is_connectable(conn):
            raise TypeError(f"{self} attempting to connect non-connectable {conn}")
        self.conns[portname] = conn
        if does_track_connected_ports(conn):
            conn.connected_ports.append(PortRef(self, portname))
        return self

    # Attach all of these to the class
    cls.__call__ = __call__
    cls.__setattr__ = __setattr__
    cls.connect = connect
    cls.__call_and_setattr_connects__ = True

    # And don't forget to return it!
    return cls


def does_call_and_setattr_connect(obj: Any) -> bool:
    """ Boolean indication of "call and setattr connects" functionality """
    return getattr(obj, "__call_and_setattr_connects__", False)


def getattr_port_refs(cls: type) -> type:
    """ Decorator to add the "__getattr__ generates PortRefs" functionality to `cls`. 

    Adds the `_port_ref` method and `__getattr__` access to it. 

    This method is *required* of `@call_and_setattr_connects` types (e.g. `Instance`s), 
    and is also included on `PortRef`s themselves, largely to support nested Bundled references. """

    # First check and fail if any of the methods to be defined here are already defined elsewhere
    defined_here = ["_port_ref", "__getattr__"]
    for key in defined_here:
        if key in cls.__dict__:
            msg = f"Invalid modification of {cls} with `@getattr_port_refs`: {key} is already defined."
            raise RuntimeError(msg)

    def _port_ref(self, key: str) -> "PortRef":
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

    def __getattr__(self, key: str) -> Any:
        """ Port access by getattr """
        if not self.__getattribute__("_initialized") or key.startswith("_"):
            # Bootstrapping phase: do regular getattrs to get started
            return object.__getattribute__(self, key)

        if key in self.__getattribute__("_specialcases"):  # Special case(s)
            return object.__getattribute__(self, key)

        # After elaboration, the fancy PortRef creation below goes away. Only return ready-made connections.
        if self.__getattribute__("_elaborated"):
            # Types without Instance-style connections return "regular getattr"
            if not does_call_and_setattr_connect(self):
                return object.__getattribute__(self, key)

            # Types with Instance-style connections pull from their `conns` dict.
            conns = self.__getattribute__("conns")
            if key in conns.keys():
                return conns[key]
            raise AttributeError(f"No attribute {key} for {self}")

        # Fell through all those cases. Fancy `PortRef` generation time!
        # Return a `PortRef`, creating one if necessary.
        return self._port_ref(key)

    cls._port_ref = _port_ref
    cls.__getattr__ = __getattr__
    cls.__getattr_port_refs__ = True

    # And don't forget to return it!
    return cls


def has_getattr_port_refs(obj: Any) -> bool:
    """ Boolean indication of "getattr port refs" functionality """
    return getattr(obj, "__getattr_port_refs__", False)
