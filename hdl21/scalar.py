from typing import Union
from decimal import Decimal
from pydantic import BaseModel

# Local Imports
from .prefix import Prefixed
from .literal import Literal


class Scalar(BaseModel):
    """
    # The `Scalar` parameter type

    Generally this means `Union[Prefixed, Literal]`,
    with some extra conversions from common built-in types, especially int, string, and float.

    `Scalar` is particularly designed for parameter-values of `Primitive`s and of simulations.
    Most such parameters "want" to be the `Prefixed` type, for reasons outlined in
    https://github.com/dan-fritchman/Hdl21#prefixed-numeric-parameters.

    They often also need a string-valued escape hatch, e.g. when referring to out-of-Hdl21 quantities
    such as parameters in external netlists, or simulation decks.
    These out-of-Hdl21 expressions are represented by the `Literal` type, a simple wrapper around `str`.

    Where possible we prefer to use the `Prefixed` variant.
    Strings and built-in numbers (int, float, Decimal) are converted to `Prefixed` inline by the `validate` method.
    All of the `validate` mechanisms work for `Scalar`s used as fields in `pydantic.dataclasses`.
    which crucially include all `hdl21.paramclass`es.
    """

    inner: Union[Prefixed, Literal]

    @classmethod
    def new(cls, inner: Union[Prefixed, Literal]) -> "Scalar":
        """Create a `Scalar` from a `Prefixed` or `Literal`.
        The (somewhat) shorthand way of calling the `Scalar` constructor
        with arguments by-order, which `pydantic.BaseModel` does not support."""
        return Scalar(inner=inner)

    @classmethod
    def validate(cls, v: Union["Scalar", "ToScalar"]) -> "Scalar":
        """Validate and convert a `ToScalar` to a `Scalar`.
        Most importantly this handles the case in which `v` is a *string*,
        which attempts conversion to a `Prefixed`,
        and falls back to a `Literal` on failure."""

        if isinstance(v, Scalar):
            return v  # Valid as-is, return it.
        if isinstance(v, (Prefixed, Literal)):
            return Scalar(inner=v)  # Also basically done

        # Now the important case
        if isinstance(v, str):
            try:  # Try to convert to a Prefixed, which internally converts to a Decimal
                inner = Prefixed(number=v)
            except Exception:  # Catch all exceptions
                inner = Literal(txt=v)
            return Scalar(inner=inner)

        # Everything else - notably including `int` and `float` - must be convertible to `Prefixed`, or fails in its validation.
        return Scalar(inner=Prefixed(number=v))

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    """
    # Math Methods
    
    Generally passed along to `self.inner`. 
    If our inner value is a `Literal`, these generally fail. 
    If it's a `Prefixed`, they should succeed. 

    Note these generally *do not* return another `Scalar`. 
    The intent of this type is really "Union[Prefixed, Literal], with some extra fancy conversions."
    And those conversions include from anything that these math ops can produce - notably `Prefixed` and `Literal`. 
    """

    def __int__(self) -> int:
        return int(self.inner)

    def __float__(self) -> float:
        return float(self.inner)

    def __mul__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__mul__(other)

    def __rmul__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__rmul__(other)

    def __truediv__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__truediv__(other)

    def __pow__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__pow__(other)

    def __add__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__add__(other)

    def __radd__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__radd__(other)

    def __sub__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__sub__(other)

    def __rsub__(self, other):
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__rsub__(other)

    # Comparison operators
    def __lt__(self, other) -> bool:
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__lt__(other)

    def __le__(self, other) -> bool:
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__le__(other)

    def __ne__(self, other) -> bool:
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__ne__(other)

    def __gt__(self, other) -> bool:
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__gt__(other)

    def __ge__(self, other) -> bool:
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__ge__(other)

    """
    # Equality and Hashing 

    Both operate directly on `inner` values. 
    This has some possibility to go haywire someday, if for example we enable `Literal` vs `Prefixed` equality tests, 
    or otherwise allow them to drop through to one another, e.g. `Prefixed.number == Decimal(str(Literal.txt))`, or similar. 
    As-is hashing and equality testing the `inner` fields works. But these two methods require a look each time we edit them. 
    """

    def __eq__(self, other) -> bool:
        if isinstance(other, Scalar):
            other = other.inner
        return self.inner.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.inner)


# Union of types convertible into `Scalar`
ToScalar = Union[Prefixed, Literal, str, int, float, Decimal]

__all__ = ["Scalar", "ToScalar"]
