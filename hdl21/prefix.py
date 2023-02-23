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
from typing import Optional, Any, Union
from pydantic import BaseModel, ValidationError, Field
from pydantic.dataclasses import dataclass


EPSILON = 20


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
        """Get the prefix from the exponent. If `exp` is not
        in the members of Prefix, returns None instead"""
        inverted = {v.value: v for v in cls.__members__.values()}

        return inverted.get(exp, None)

    @classmethod
    def closest(cls, exp: Any) -> Optional["Prefix"]:
        return min(cls.__members__.values(), key=lambda x: abs(x.value - exp))

    def __mul__(self, other: Any):

        if isinstance(other, Prefix):
            # Prefix times Prefix, eg. `p * M == µ`
            targ = self.value + other.value
            return e(targ)

        return NotImplemented

    def __rmul__(self, other: Any):
        """Right-hand-side multiplication operator, e.g. `5 * µ`."""

        if isinstance(other, (Decimal, float, int, str)):
            # The usual use-case, e.g. `5 * µ`
            return Prefixed(number=other, prefix=self)

        if isinstance(other, Prefixed):
            # Prefixed times Prefix, e.g. `(5 * n) * G`
            targ = self.value + other.prefix.value
            exptemp = e(targ)

            # Scale the other number
            new_num = other.number * Decimal(10) ** (targ - exptemp.symbol.value)

            # And create a corresponding `Prefixed`
            return Prefixed.new(new_num, exptemp.symbol)

        return NotImplemented

    def __truediv__(self, other: Any):
        """Division operator, e.g. `p / µ == µ`
        typical usage to evaluate prefix arithmetic"""

        if isinstance(other, Prefix):

            # Prefix divided by Prefix, eg. `p / M == a`
            targ = self.value - other.value
            return e(targ)

        return NotImplemented

    def __pow__(self, other: Any):
        """Power operator, e.g. `K ** 2 == M
        typical usage to evaluate prefix raised to integer powers"""

        if isinstance(other, (str, int, float, Decimal)):
            # Prefix raised to power of number, eg. `µ ** 4 == y`
            targ = self.value * Decimal(str(other))
            return e(targ)

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


class Prefixed(BaseModel):
    """
    # Prefixed

    Combination of a literal value and a unit-indicating prefix.
    Colloquially, the numbers in expressions like "5ns", "11MV", and "1µA"
    are represented as `Prefixed`.
    """

    # Numeric Portion. See the long note above.
    number: Decimal
    # Enumerated SI Prefix. Defaults to unity.
    prefix: Prefix = Field(default=Prefix.UNIT)

    @classmethod
    def new(cls, number: Decimal, prefix: Prefix = Prefix.UNIT) -> "Prefixed":
        """Create a new Prefixed number.
        Alias for `Prefixed(number=number, prefix=prefix), and a (slight) shorthand
        for using arguments by-position, which `pydantic.BaseModel` does not support."""
        return cls(number=number, prefix=prefix)

    @classmethod
    def validate(cls, v: Union["Prefixed", "ToPrefixed"]) -> "Prefixed":
        """Validate `v` as a `Prefixed` number, or convert to `Prefixed` if applicable.
        While usable elsewhere, `validate` is primarily intended for use in type-validated
        dataclass trees, such as those generated in `paramclass`es."""

        if isinstance(v, Prefixed):
            return v  # Valid as-is, return it.
        if isinstance(v, Decimal):
            return Prefixed(number=v)  # Also pretty much done
        # Convert the remaining convertible types to `Decimal` inline
        if isinstance(v, (int, float)):
            # Note that, like `pydantic`, we convert numeric types to `str` before passing to `Decimal`.
            return Prefixed(number=Decimal(str(v)))
        if isinstance(v, str):
            return Prefixed(number=Decimal(v))
        raise ValidationError(f"Cannot convert {v} to Prefixed number")

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    def __hash__(self):
        return hash((self.number, self.prefix))

    def __int__(self) -> int:
        return int(self.number) * 10**self.prefix.value

    def __float__(self) -> float:
        """Convert to float"""
        return float(self.number) * 10**self.prefix.value

    def __mul__(self, other) -> "Prefixed":
        if isinstance(other, Prefixed):
            return (self.number * other.number * self.prefix * other.prefix).scale()
        elif not isinstance(other, (str, int, float, Decimal)):
            return NotImplemented
        return Prefixed.new(self.number * Decimal(str(other)), self.prefix).scale()

    def __rmul__(self, other) -> "Prefixed":
        if isinstance(other, Prefixed):
            return (self.number * other.number * self.prefix * other.prefix).scale()
        elif not isinstance(other, (str, int, float, Decimal)):
            return NotImplemented
        return Prefixed.new(self.number * Decimal(str(other)), self.prefix).scale()

    def __truediv__(self, other) -> "Prefixed":
        if isinstance(other, Prefixed):
            return ((self.number / other.number) * (self.prefix / other.prefix)).scale()
        elif not isinstance(other, (str, int, float, Decimal)):
            return NotImplemented
        return Prefixed.new(self.number / Decimal(str(other)), self.prefix).scale()

    def __pow__(self, other) -> "Prefixed":
        if not isinstance(other, (str, int, float, Decimal)):
            return NotImplemented
        return (
            self.number ** Decimal(str(other)) * (self.prefix ** Decimal(str(other)))
        ).scale()

    def __add__(self, other: "Prefixed") -> "Prefixed":
        if not isinstance(other, Prefixed):
            return NotImplemented
        return _add(lhs=self, rhs=other).scale()

    def __radd__(self, other: "Prefixed") -> "Prefixed":
        if not isinstance(other, Prefixed):
            return NotImplemented
        return _add(lhs=other, rhs=self).scale()

    def __sub__(self, other: "Prefixed") -> "Prefixed":
        if not isinstance(other, Prefixed):
            return NotImplemented
        return _subtract(lhs=self, rhs=other).scale()

    def __rsub__(self, other: "Prefixed") -> "Prefixed":
        if not isinstance(other, Prefixed):
            return NotImplemented
        return _subtract(lhs=other, rhs=self).scale()

    def scale(self, prefix: Prefix = None) -> "Prefixed":
        """Scale to a new `Prefix`"""
        if isinstance(prefix, Prefix):
            newnum = self.number * Decimal(10) ** (self.prefix.value - prefix.value)
            return Prefixed.new(newnum, prefix)
        else:
            newpref = Prefix.closest(abs(self.number).log10() + self.prefix.value)
            return self.scale(newpref)

    def __repr__(self) -> str:
        return f"{self.number}*{self.prefix.name}"

    # Comparison operators that respect class convention
    def __lt__(self, other) -> bool:
        lhs, rhs = _scale_to_smaller(self, other)
        return round(lhs.number, EPSILON) < round(rhs.number, EPSILON)

    def __le__(self, other) -> bool:
        lhs, rhs = _scale_to_smaller(self, other)
        return round(lhs.number, EPSILON) <= round(rhs.number, EPSILON)

    def __eq__(self, other) -> bool:
        lhs, rhs = _scale_to_smaller(self, other)
        return round(lhs.number, EPSILON) == round(rhs.number, EPSILON)

    def __ne__(self, other) -> bool:
        lhs, rhs = _scale_to_smaller(self, other)
        return round(lhs.number, EPSILON) != round(rhs.number, EPSILON)

    def __gt__(self, other) -> bool:
        lhs, rhs = _scale_to_smaller(self, other)
        return round(lhs.number, EPSILON) > round(rhs.number, EPSILON)

    def __ge__(self, other) -> bool:
        lhs, rhs = _scale_to_smaller(self, other)
        return round(lhs.number, EPSILON) >= round(rhs.number, EPSILON)


# Union of the types which can be converted to `Prefixed`
ToPrefixed = Union[int, float, str, Decimal]


def _add(lhs: Prefixed, rhs: Prefixed) -> Prefixed:
    """`Prefixed` Addition"""
    if lhs.prefix == rhs.prefix:
        return Prefixed.new(lhs.number + rhs.number, lhs.prefix)

    # Different prefix values. Scale to the smaller of the two
    smaller = lhs.prefix if lhs.prefix.value < rhs.prefix.value else rhs.prefix
    newnum = lhs.scale(smaller).number + rhs.scale(smaller).number
    return Prefixed.new(newnum, smaller)


def _subtract(lhs: Prefixed, rhs: Prefixed) -> Prefixed:
    """`Prefixed` Subtraction"""
    if lhs.prefix == rhs.prefix:
        return Prefixed.new(lhs.number - rhs.number, lhs.prefix)

    # Different prefix values. Scale to the smaller of the two
    smaller = lhs.prefix if lhs.prefix.value < rhs.prefix.value else rhs.prefix
    newnum = lhs.scale(smaller).number - rhs.scale(smaller).number
    return Prefixed.new(newnum, smaller)


def _scale_to_smaller(lhs: Prefixed, rhs: Prefixed):
    smaller = lhs.prefix if lhs.prefix.value < rhs.prefix.value else rhs.prefix
    return lhs.scale(smaller), rhs.scale(smaller)


# Common prefixes as single-character identifiers, and exposed in the module namespace.
y = YOCTO = Prefix.YOCTO
z = ZEPTO = Prefix.ZEPTO
a = ATTO = Prefix.ATTO
f = FEMTO = Prefix.FEMTO
p = PICO = Prefix.PICO
n = NANO = Prefix.NANO
µ = MICRO = Prefix.MICRO
m = MILLI = Prefix.MILLI
c = CENTI = Prefix.CENTI
d = DECI = Prefix.DECI
D = DECA = Prefix.DECA
K = KILO = Prefix.KILO
M = MEGA = Prefix.MEGA
G = GIGA = Prefix.GIGA
T = TERA = Prefix.TERA
P = PETA = Prefix.PETA
E = EXA = Prefix.EXA
Z = ZETTA = Prefix.ZETTA
Y = YOTTA = Prefix.YOTTA

# The Unit prefix doesn't get a single-character name, since it's kinda confusing with `µ`,
# but is exposed at module scope.
UNIT = Prefix.UNIT


@dataclass
class Exponent:
    """
    # Exponent

    Exponent is a helper class that aids Prefixed arithmetic in a way that is intuitive
    for users, such as allowing arbitrary powers, division and other functionality.

    A important feature of the design of Exponent is that it is a helper class: so it may
    only be invoked by other classes and can only interact with itself and Decimal/int/floats.
    """

    symbol: Prefix  # Prefix symbol for calculation
    residual: Decimal = Decimal(0)  # Prefix

    @classmethod
    def from_exp(self, exp: Any):

        out_symbol = Prefix.closest(exp)
        out_residual = Decimal(str(exp)) - out_symbol.value
        return Exponent(out_symbol, out_residual)

    def __mul__(self, other: Optional["Exponent"]) -> Optional["Exponent"]:

        if isinstance(other, Exponent):
            # Exponent(n,0.3) * Exponent(K,0.4) == e(-8.7) * e(3.4) = e(-5.3)
            return Exponent.from_exp(
                self.symbol.value + other.symbol.value + self.residual + other.residual
            )

        return NotImplemented

    def __rmul__(self, other: Any) -> Prefixed:

        if isinstance(other, (str, int, float, Decimal)):
            # 16 * Exponent(Symbol.UNIT,0.25) == 2 * Prefix.UNIT

            out_number = Decimal(str(other)) * Decimal(10) ** self.residual

            return Prefixed.new(out_number, self.symbol)

        elif isinstance(other, Prefixed):
            # 2 * Prefix.UNIT * Exponent(Symbol.KILO,0) == 2 * Prefix.KILO
            temp_exp = e(other.prefix.value)
            temp_exp *= self
            return other.number * temp_exp

        return NotImplemented

    def __truediv__(self, other: Any) -> Optional["Exponent"]:

        if isinstance(other, (str, int, float, Decimal)):
            # Exponent(1) / 2 = Exponent(log(5))
            inv_other = Decimal(1) / Decimal(str(other))
            return inv_other * self

        elif isinstance(other, Exponent):
            return self * (other**-1)

        return NotImplemented

    def __pow__(self, other: Any) -> Optional["Exponent"]:

        if isinstance(other, (str, int, float, Decimal)):
            # Exponent(0.25) ** 4 == Exponent(1)
            return Exponent.from_exp(
                ((self.symbol.value + self.residual) * Decimal(str(other)))
            )

        return NotImplemented

    def __repr__(self) -> str:
        return f"e({self.symbol.value+self.residual})"


def e(exp: Any) -> Exponent:
    """# Exponential `Prefix` Creation

    Returns an `Exponent` for power-of-ten exponent `exp`.

    In many cases HDL parameters must be non-integer values,
    e.g. `1nm`, but using `float` can prove undesirable
    as rounding errors can turn them into subtly different values.
    The `e()` function is most commonly useful with multiplication,
    to create "floating point" values such as `11 * e(-9)`.
    """

    if isinstance(exp, (str, int, float, Decimal)):

        out_symbol = Prefix.closest(exp)
        out_residual = Decimal(str(exp)) - out_symbol.value

        return Exponent(out_symbol, out_residual)

    return NotImplemented


# Star-imports *do not* include the single-character names `µ`, `e`, et al.
# They can be explicityle imported from `hdl21.prefix` instead.
__all__ = ["Prefix", "Prefixed", "Exponent"]
