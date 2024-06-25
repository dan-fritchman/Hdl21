# Std-Lib imports
from typing import Set, Union, Optional

# Local imports
from .datatype import datatype, AllowArbConfig
from .connect import connectable
from .sliceable import sliceable
from .concat import concatable
from .instance import _Instance


@concatable
@sliceable
@connectable
@datatype(config=AllowArbConfig)
class PortRef:
    """
    # PortRef
    Reference to a Port
    Created from a combination of a parent `Instance` and a port-name.
    """

    # Core fields: the Instance and port name
    inst: _Instance
    portname: str

    __slots__ = (
        "inst",
        "portname",
        "_connected_ports",
        "resolved",
        "_slices",
        "_concats",
        "_width",
    )

    def __post_init__(self):
        # Inner management data
        self._connected_ports: Set[PortRef] = set()
        self.resolved: Union[None, "Signal", "BundleInstance"] = None
        self._slices: Set["Slice"] = set()
        self._concats: Set["Concat"] = set()
        self._width: Optional[int] = None

    def __eq__(self, other) -> bool:
        """Port-reference equality requires *identity* between instances
        (and of course equality of port-name)."""
        try:
            return self.inst is other.inst and self.portname == other.portname
        except AttributeError:
            return False

    def __hash__(self):
        """Hash references as the tuple of their instance-address and name"""
        return hash((id(self.inst), self.portname))
