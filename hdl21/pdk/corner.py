"""
# PDK Corners
"""

from enum import Enum, auto
from pydantic.dataclasses import dataclass


class Corner(Enum):
    """# Enumerated Generic Corners

    Values of the `Corner` enum can mean either the variations in a particular device,
    e.g. the "slow" versus "fast" variations of a poly resistor,
    or can just as oftern refer to a set of such variations within a given technology.

    In the latter case `Corner` values are often expanded by PDK-level code to include each
    constituent device variation. For example `my.pdk.corner(Corner.FAST)` might expand to
    definitions of "fast" Cmos transistors, resistors, and capacitors."""

    TYP = auto()
    FAST = auto()
    SLOW = auto()

    def __repr__(self) -> str:
        return self.name


class CornerType(Enum):
    """Enumerated Types of PDK Content to be Corner-Varied"""

    MOS = auto()  # A single transistor type, e.g. NMOS
    CMOS = auto()  # A pair of transistors, e.g. NMOS/PMOS
    RES = auto()  # Resistors
    CAP = auto()  # Capacitors

    def __repr__(self) -> str:
        return self.name


@dataclass
class CmosCornerPair:
    """Cmos Corner Pair"""

    nmos: Corner
    pmos: Corner


class CmosCorner(Enum):
    """# Cmos Corner
    All values are `CmosCornerPair` objects.
    Naming convention is (Nmos, Pmos), e.g. "FS" is fast-N, slow-P."""

    TT = CmosCornerPair(Corner.TYP, Corner.TYP)
    FF = CmosCornerPair(Corner.FAST, Corner.FAST)
    SS = CmosCornerPair(Corner.SLOW, Corner.SLOW)
    FS = CmosCornerPair(Corner.FAST, Corner.SLOW)
    SF = CmosCornerPair(Corner.SLOW, Corner.FAST)

    def __repr__(self) -> str:
        return self.name
