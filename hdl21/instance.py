""" 
# Hdl21 Hierarchical Instances 

Create instances of Modules, Generators, and Primitives in a hierarchy
"""

from typing import Optional, Union, List, Any, Dict

# Local imports
from .connect import (
    connectable,
    track_connected_ports,
    call_and_setattr_connects,
    getattr_port_refs,
)


@track_connected_ports
@connectable
class PortRef:
    """ Reference to a Port 
    Created from a combination of a parent `inst` and a port-name. """

    _specialcases = [
        "inst",
        "portrefs",
        "connect",
        "connected_ports",
        "_port_ref",
        "_module",
        "_resolved",
        "_elaborated",
        "_initialized",
    ]

    def __init__(
        self, inst: Union["Instance", "InstArray"], portname: str,
    ):
        self.inst = inst
        self.portname = portname
        self.portrefs: Dict[str, "PortRef"] = dict()
        # Connected port references
        self.connected_ports: List["PortRef"] = []
        self._elaborated = False
        self._initialized = True

    def __eq__(self, other) -> bool:
        """ Port-reference equality requires *identity* between instances 
        (and of course equality of port-name). """
        return self.inst is other.inst and self.portname == other.portname

    def __hash__(self):
        """ Hash references as the tuple of their instance-address and name """
        return hash((id(self.inst), self.portname))


class _Instance:
    """ Shared base class for Instance-like types (Instance, InstArray) """

    def __init__(
        self, of: "Instantiable", *, name: Optional[str] = None,
    ):
        from .instantiable import is_instantiable

        if not is_instantiable(of):
            raise RuntimeError(f"Invalid Instance of {of}")

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


@call_and_setattr_connects
@getattr_port_refs
class Instance(_Instance):
    """ Hierarchical Instance of another Module or Generator """

    _specialcases = [
        "name",
        "of",
        "conns",
        "portref",
        "portrefs",
        "connect",
        "_port_ref",
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


@call_and_setattr_connects
@getattr_port_refs
class InstArray(_Instance):
    """ Array of `n` Instances """

    _specialcases = [
        "name",
        "of",
        "conns",
        "portref",
        "portrefs",
        "_port_ref",
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

    def __getitem__(self, idx: int):
        return RuntimeError(f"Illegal indexing into Array {self}")

    def __setitem__(self, _idx: Any, _val: Any):
        return RuntimeError(f"Illegal indexing into Array {self}")


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
