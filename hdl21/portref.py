from dataclasses import field
from typing import Set, Union

# Local imports
from .datatype import datatype
from .connect import connectable, track_connected_ports
from .instance import _Instance


@track_connected_ports
@connectable
@datatype
class PortRef:
    """# PortRef
    Reference to a Port
    Created from a combination of a parent `inst` and a port-name."""

    # Core fields: the Instance and port name
    inst: _Instance
    portname: str

    def __post_init_post_parse__(self):
        self.connected_ports: Set[PortRef] = set()
        self.resolved: Union[None, "Signal", "BundleInstance"] = None

    def __eq__(self, other) -> bool:
        """Port-reference equality requires *identity* between instances
        (and of course equality of port-name)."""
        return self.inst is other.inst and self.portname == other.portname

    def __hash__(self):
        """Hash references as the tuple of their instance-address and name"""
        return hash((id(self.inst), self.portname))
