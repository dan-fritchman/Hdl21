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
    def validate(cls, v: Union["Scalar", "ToScalar"]) -> "Scalar":
        """Validate and convert a `ToScalar` to a `Scalar`.
        Most importantly this handles the case in which `v` is a *string*,
        which attempts conversion to a `Prefixed`,
        and falls back to a `Literal` on failure."""

        if isinstance(v, Scalar):
            return v  # Done validating
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


# Union of types convertible into `Scalar`
ToScalar = Union[Prefixed, Literal, str, int, float, Decimal]

__all__ = ["Scalar", "ToScalar"]
