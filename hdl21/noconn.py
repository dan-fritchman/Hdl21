"""
# No-Connect

Special placeholder connectable-object which indicates "unconnected" Ports,
typically unconnected outputs.

An optional `name` field allows guidance for external netlisting,
for cases in which consistent naming is desirable (e.g. for waveform probing).
"""

from dataclasses import field
from typing import Callable, Optional, List, Union, Set
from pydantic.dataclasses import dataclass

# Local imports
from .datatype import datatype
from .connect import connectable, track_connected_ports
from .portref import PortRef


@track_connected_ports
@connectable
@datatype
class NoConn:
    """
    # No-Connect

    Special placeholder connectable-object which indicates "unconnected" Ports,
    typically unconnected outputs.

    An optional `name` field allows guidance for external netlisting,
    for cases in which consistent naming is desirable (e.g. for waveform probing).
    """

    name: Optional[str] = None

    # Internal, ideally private fields
    # Connected port references
    connected_ports: Set[PortRef] = field(init=False, repr=False, default_factory=set)

    def __eq__(self, other: "NoConn") -> bool:
        """`NoConn`s are "equal" only if identical objects."""
        return self is other

    def __hash__(self) -> int:
        """`NoConn`s are "equal" only if identical objects."""
        return hash(id(self))
