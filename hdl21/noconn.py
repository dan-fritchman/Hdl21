"""
# No-Connect

Special placeholder connectable-object which indicates "unconnected" Ports,
typically unconnected outputs.

An optional `name` field allows guidance for external netlisting,
for cases in which consistent naming is desirable (e.g. for waveform probing).
"""

from typing import Optional, Set

# Local imports
from .datatype import datatype
from .connect import connectable
from .concat import concatable
from .portref import PortRef


@concatable
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

    def __post_init_post_parse__(self) -> None:
        # Internal management data
        # Connected port references
        self._connected_ports: Set[PortRef] = set()

    def __eq__(self, other: "NoConn") -> bool:
        """`NoConn`s are "equal" only if identical objects."""
        return self is other

    def __hash__(self) -> int:
        """`NoConn`s are "equal" only if identical objects."""
        return hash(id(self))
