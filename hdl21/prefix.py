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
from typing import Optional, Any


class Prefix(Enum):
    """Enumerated Unit Prefixes
    Values are equal to the associated power-of-ten exponent."""

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
    UNIT = 0  # No prefix
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
        """Get the prefix from the exponent.
        Returns None if the exponent does not correspond to a valid prefix.
        FIXME: apply scaling here for non first class exponents."""
        inverted = {v.value: v for v in cls.__members__.values()}
        return inverted.get(exp, None)

    def __rmul__(self, other: Any):
        """Right-hand-side multiplication operator, e.g. `5 * µ`."""

        if isinstance(other, (Decimal, float, int, str)):
            # The usual use-case, e.g. `5 * µ`
            return Prefixed(other, self)

        if isinstance(other, Prefixed):
            # Prefixed times Prefix, e.g. `(5 * n) * G`
            targ = self.value + other.prefix.value
            prefix = Prefix.from_exp(targ)
            if prefix is not None:
                return Prefixed(other.number, prefix)

            # Didn't land on a supported prefix. Scale to the nearest smaller one.
            closest = max(
                [v.value for v in type(self).__members__.values() if v.value < targ]
            )
            # Scale the other number
            new_num = other.number * 10 ** (targ - closest)
            # And create a corresponding `Prefixed`
            return Prefixed(number=new_num, prefix=Prefix.from_exp(closest))

        return NotImplemented


"""
# Note on Numeric Types 

`Prefixed` supports a sole type for its `number` field: the standard library's `Decimal`. 
One might wonder why it does not include `int` and `float` as well, or perhaps 
some other numeric-like types. 

This boils down to limitations in validation. Previous versions of `Prefixed` have 
used a `Number` union-type along these lines:
```
Number = Union[Decimal, float, int]
```
This is nominally handy, but results in many values being converted among these types, 
often where one may not expect. 
The pydantic docs are clear about their limitations in this respect: 
https://pydantic-docs.helpmanual.io/usage/types/#unions

These limitations include the fact that despite being declared in list-like 
"ordered" syntax, union-types do not have orders in the Python standard library. 
So even interpreting `Union[Decimal, float, int]` as "prefer Decimal, use float 
and then int if that (for whatever reason) doesn't work" fails, 
since the `Union` syntax can be reordered arbitrarily by the language. 

The other clear alternative is not doing runtime type-validation of `Prefixed`, 
or of classes which instantiate them. Prior versions also tried this, 
to fairly confounding results. Incorporating standard-library `dataclasses` 
as members of larger `pydantic.dataclasses` seems to *work* - i.e. it does not 
produce `ValidationError`s or similar - but ultimately with enough of them, 
triggers some highly inscrutable errors in the standard-library methods. 

So: all `Decimal`, all `pydantic.dataclasses`.
"""

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)  # `frozen` for hashability
class Prefixed:
    """
    # Prefixed

    Combination of a literal value and a unit-indicating prefix.
    Colloquially, the numbers in expressions like "5ns", "11MV", and "1µA"
    are represented as `Prefixed`.
    """

    number: Decimal  # Numeric Portion. See the long note above.
    prefix: Prefix = Prefix.UNIT  # Enumerated SI Prefix. Defaults to unity.

    def __float__(self) -> float:
        """Convert to float"""
        return float(self.number) * 10**self.prefix.value

    def __mul__(self, other) -> "Prefixed":
        if not isinstance(other, (int, float, Decimal)):
            return NotImplemented
        return Prefixed(self.number * other, self.prefix)

    def __rmul__(self, other) -> "Prefixed":
        if not isinstance(other, (int, float, Decimal)):
            return NotImplemented
        return Prefixed(self.number * other, self.prefix)

    def __truediv__(self, other) -> "Prefixed":
        if not isinstance(other, (int, float, Decimal)):
            return NotImplemented
        return Prefixed(self.number / other, self.prefix)

    def __add__(self, other: "Prefixed") -> "Prefixed":
        return _add(lhs=self, rhs=other)

    def __radd__(self, other: "Prefixed") -> "Prefixed":
        return _add(lhs=other, rhs=self)

    def __sub__(self, other: "Prefixed") -> "Prefixed":
        return _subtract(lhs=self, rhs=other)

    def __rsub__(self, other: "Prefixed") -> "Prefixed":
        return _subtract(lhs=other, rhs=self)

    def scaleto(self, prefix: Prefix) -> "Prefixed":
        """Scale to a new `Prefix`"""
        newnum = self.number * 10 ** (self.prefix.value - prefix.value)
        return Prefixed(newnum, prefix)

    def __repr__(self) -> str:
        return f"{self.number}*{self.prefix.name}"

    # FIXME: add comparison operations


def _add(lhs: Prefixed, rhs: Prefixed) -> Prefixed:
    """`Prefixed` Addition"""
    if not isinstance(lhs, Prefixed) or not isinstance(rhs, Prefixed):
        return NotImplemented

    if lhs.prefix == rhs.prefix:
        return Prefixed(lhs.number + rhs.number, lhs.prefix)

    # Different prefix values. Scale to the smaller of the two
    smaller = lhs.prefix if lhs.prefix.value < rhs.prefix.value else rhs.prefix
    newnum = lhs.scaleto(smaller).number + rhs.scaleto(smaller).number
    return Prefixed(newnum, smaller)


def _subtract(lhs: Prefixed, rhs: Prefixed) -> Prefixed:
    """`Prefixed` Subtraction"""
    if not isinstance(lhs, Prefixed) or not isinstance(rhs, Prefixed):
        return NotImplemented

    if lhs.prefix == rhs.prefix:
        return Prefixed(lhs.number - rhs.number, lhs.prefix)

    # Different prefix values. Scale to the smaller of the two
    smaller = lhs.prefix if lhs.prefix.value < rhs.prefix.value else rhs.prefix
    newnum = lhs.scaleto(smaller).number - rhs.scaleto(smaller).number
    return Prefixed(newnum, smaller)


# Common prefixes as single-character identifiers, and exposed in the module namespace.
f = FEMTO = Prefix.FEMTO
p = PICO = Prefix.PICO
n = NANO = Prefix.NANO
µ = MICRO = Prefix.MICRO
m = MILLI = Prefix.MILLI
K = KILO = Prefix.KILO
M = MEGA = Prefix.MEGA
G = GIGA = Prefix.GIGA
T = TERA = Prefix.TERA
P = PETA = Prefix.PETA
# The Unit prefix doesn't get a single-character name, since it's kinda confusing with `µ`,
# but is exposed at module scope.
UNIT = Prefix.UNIT


def e(exp: int) -> Optional[Prefix]:
    """# Exponential `Prefix` Creation

    Returns a `Prefix` for power-of-ten exponent `exp`.

    In many cases HDL parameters must be non-integer values,
    e.g. `1nm`, but using `float` can prove undesirable
    as rounding errors can turn them into subtly different values.
    The `e()` function is most commonly useful with multiplication,
    to create "floating point" values such as `11 * e(-9)`.
    """
    return Prefix.from_exp(exp)


# Star-imports *do not* include the single-character names `µ`, `e`, et al.
# They can be explicityle imported from `hdl21.prefix` instead.
__all__ = ["Prefix", "Prefixed"]
