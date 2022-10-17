from copy import copy
from typing import Set, Union, Optional

# Local imports
from .datatype import datatype
from .connect import connectable
from .sliceable import sliceable
from .concat import concatable
from .instance import _Instance


@concatable
@sliceable
@connectable
@datatype
class PortRef:
    """
    # PortRef
    Reference to a Port
    Created from a combination of a parent `Instance` and a port-name.
    """

    # Core fields: the Instance and port name
    inst: _Instance
    portname: str

    def __post_init_post_parse__(self):
        # Inner management data
        self._connected_ports: Set[PortRef] = set()
        self.resolved: Union[None, "Signal", "BundleInstance"] = None
        self._slices: Set["Slice"] = set()
        self._concats: Set["Concat"] = set()
        self._width: Optional[int] = None

    def __eq__(self, other) -> bool:
        """Port-reference equality requires *identity* between instances
        (and of course equality of port-name)."""
        if not isinstance(other, PortRef):
            return False
        return self.inst is other.inst and self.portname == other.portname

    def __hash__(self):
        """Hash references as the tuple of their instance-address and name"""
        return hash((id(self.inst), self.portname))
