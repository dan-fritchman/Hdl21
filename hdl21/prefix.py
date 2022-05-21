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

# Note the types here - particularly anything touching the `Number` union-type,
# *do not* use Pydantic. It doesn't have great control over which variant
# actually makes it through its validation process, as described here:
# https://pydantic-docs.helpmanual.io/usage/types/#unions
#
# For `Number` and similar, this often causes unexpected conversions
# between int, float, and Decimal. Everything instantiating a `Number`,
# including the `Prefixed` type defined here, must use the standard-library
# `dataclass` instead.
from dataclasses import dataclass

# `Number` shorthand for the union of types accepted as the numeric parts of `Prefixed`s
Number = Union[Decimal, float, int]


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

        if isinstance(other, get_args(Number)):  # The usual use-case, e.g. `5 * µ`
            return Prefixed(other, self)

        if isinstance(other, Prefixed):
            # Prefixed times Prefix, e.g. `(5 * n) * G`
            targ = self.value + other.prefix.value
            prefix = Prefix.from_exp(targ)
            if prefix is not None:
                return Prefixed(other.value, prefix)

            # Didn't land on a supported prefix. Scale to the nearest smaller one.
            closest = max(
                [v.value for v in type(self).__members__.values() if v.value < targ]
            )
            # Scale the other number
            new_num = other.number * 10 ** (targ - closest)
            # And create a corresponding `Prefixed`
            return Prefixed(number=new_num, prefix=Prefix.from_exp(closest))

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
