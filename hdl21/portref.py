from dataclasses import field
from typing import Set, Dict

# Local imports
from .datatype import datatype
from .connect import connectable, track_connected_ports
from .instance import _Instance


@track_connected_ports
@connectable
@datatype
class PortRef:
    """ # PortRef
    Reference to a Port 
    Created from a combination of a parent `inst` and a port-name. """

    # Core fields: the Instance and port name
    inst: _Instance
    portname: str

    # Internal, ideally private, fields
    portrefs: Dict[str, "PortRef"] = field(default_factory=dict, init=False, repr=False)
    connected_ports: Set["PortRef"] = field(default_factory=set, init=False, repr=False)

    def __eq__(self, other) -> bool:
        """ Port-reference equality requires *identity* between instances 
        (and of course equality of port-name). """
        return self.inst is other.inst and self.portname == other.portname

    def __hash__(self):
        """ Hash references as the tuple of their instance-address and name """
        return hash((id(self.inst), self.portname))
