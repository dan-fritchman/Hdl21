"""
# Metric Prefixes

Defines the `Prefix` enumeration of SI unit-prefixes, 
and the `Prefixed` combination of a `Prefix` and a literal value. 

Common prefixes such as µ (micro), n (nano), and K (kilo) 
are also exposed as single-character identifiers.
Most commonly these can be used with the multiplication operator 
in expressions such as `5 * n`, `11 * M`, and `1 * µ`.

For generation of other prefixes an `e()` function allows for syntax similar to 
typical floating-point value generation. This is again most commonly useful in conjunction 
with the multiplication operator, to construct values such as `11 * e(-21)`. 

"""

from enum import Enum
from decimal import Decimal
from typing import Optional, Any, Union, get_args

from pydantic.dataclasses import dataclass

# `Number` shorthand for the union of types accepted as the numeric parts of `Prefixed`s
Number = Union[int, float, Decimal]


class Prefix(Enum):
    """ Enumerated Unit Prefixes
    Values are equal to the associated power-of-ten exponent. """

    YOCTO = -24
    ZEPTO = -21
    ATTO = -18
    FEMTO = -15
    PICO = -12
    NANO = -9
    MICRO = -6
    MILLI = -3
    CENTI = -2
    DECI = -1
    DECA = 1
    HECTO = 2
    KILO = 3
    MEGA = 6
    GIGA = 9
    TERA = 12
    PETA = 15
    EXA = 18
    ZETTA = 21
    YOTTA = 24

    @classmethod
    def from_exp(cls, exp: int) -> Optional["Prefix"]:
        """ Get the prefix from the exponent.
        Returns None if the exponent does not correspond to a valid prefix. """
        inverted = {v.value: v for v in cls.__members__.values()}
        return inverted.get(exp, None)

    def __rmul__(self, other: Any):
        """ Right-hand-side multiplication operator, e.g. `5 * µ`. """
        if isinstance(other, Prefixed):
            prefix = Prefix.from_exp(self.value + other.prefix.value)
            if prefix is None:
                # FIXME: scale to the nearest prefix
                msg = f"Prefix mult scaling for {self} and {other.prefix}"
                raise NotImplementedError(msg)
            return Prefixed(other.value, prefix)
        if isinstance(other, get_args(Number)):
            return Prefixed(other, self)
        return NotImplemented


@dataclass
class Prefixed:
    """ Combination of a literal value and a unit-indicating prefix. 
    Colloquially, the numbers in expressions like "5ns", "11MV", and "1µA" 
    are represented as `Prefixed`. """

    number: Number
    prefix: Prefix

    def __float__(self) -> float:
        """ Convert to float """
        return float(self.number) * 10 ** self.prefix.value


# Common prefixes as single-character identifiers.
f = Prefix.FEMTO
p = Prefix.PICO
n = Prefix.NANO
µ = Prefix.MICRO
m = Prefix.MILLI
K = Prefix.KILO
M = Prefix.MEGA
G = Prefix.GIGA
T = Prefix.TERA
P = Prefix.PETA


def e(exp: int) -> Optional[Prefix]:
    """ # Exponential `Prefix` Creation 
    
    Returns a `Prefix` for power-of-ten exponent `exp`. 

    In many cases HDL parameters must be non-integer values, 
    e.g. `1nm`, but using `float` can prove undesirable 
    as rounding errors can turn them into subtly different values. 
    The `e()` function is most commonly useful with multiplication, 
    to create "floating point" values such as `11 * e(-9)`. 
    """
    return Prefix.from_exp(exp)


# Star-imports *do not* include the single-character names `µ`, `e`, et al.
# They can be explicityle imported from `hdl21.units` instead.
__all__ = ["Prefix", "Prefixed"]
