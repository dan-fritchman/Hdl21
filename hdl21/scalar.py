from typing import Union
from decimal import Decimal
from pydantic import BaseModel

# Local Imports
from .prefix import Prefixed
from .literal import Literal


# Union of types convertible into `Scalar`
ToScalar = Union[Prefixed, Literal, str, int, float, Decimal]


class Scalar(BaseModel):
    """
    # The `Scalar` parameter type

    Generally this means
    ````python
    Union[Prefixed, Literal]
    ```
    with built-in automatic conversions from each of:
    ```python
    [str, int, float, Decimal]
    ```
    when used in `paramclass` definitions.

    `Scalar` is particularly designed for parameter-values of `Primitive`s and of simulations.
    Most such parameters "want" to be the `Prefixed` type, for reasons outlined in
    https://github.com/dan-fritchman/Hdl21#prefixed-numeric-parameters.

    They often also need a string-valued escape hatch, e.g. when referring to out-of-Hdl21 quantities
    such as parameters in external netlists or simulation decks.
    These out-of-Hdl21 expressions are represented by the `Literal` type, a simple wrapper around `str`.

    Where possible `Scalar` prefers to use the `Prefixed` variant.
    Strings and built-in numbers (int, float, Decimal) are converted to `Prefixed` inline by the `validate` method.
    All of the `validate` mechanisms work for `Scalar`s used as fields in `pydantic.dataclasses`.
    which crucially include all `hdl21.paramclass`es.

    While defined as a type, `Scalar` is not instantiable.
    It is really a class-based statement of `Union[Prefixed, Literal]`, with class methods to aid in validation.

    If writing "primitive-like" parameters - e.g. those that go into SPICE simulations,
    or are provided to PDK-level devices, it is very likely that you will want to:

    * Use `Scalar` as a parameter type, i.e. the `dtype` field of `Param`s.
    * Never actually instantiate a `Scalar` directly, including for its default value.

    Example:

    ```python
    import hdl21 as h
    from hdl21.prefix import NANO, µ
    from decimal import Decimal

    @h.paramclass
    class MyMosParams:
        w = h.Param(dtype=h.Scalar, desc="Width", default=1e-6) # Default `float` converts to a `Prefixed`
        l = h.Param(dtype=h.Scalar, desc="Length", default="w/5") # Default `str` converts to a `Literal`

    # Example instantiations
    MyMosParams(w=Decimal(1e-6), l=3*µ)
    MyMosParams(w=h.Literal("sim_param_width"), l=h.Prefixed.new(20, NANO))
    MyMosParams(w="11*l", l=11)
    ```
    """

    # The Pydantic "custom root types" feature is really what makes this work:
    # https://docs.pydantic.dev/latest/usage/models/#custom-root-types

    __root__: Union[Prefixed, Literal]

    def __init__(self, *_, **__):
        # Brick any attempts to create instances
        msg = f"Invalid attempt to instantiate a `Scalar` directly. "
        msg += f"Create either of its variants `Prefixed` or `Literal` instead, "
        msg += f"or use their built-in conversions from strings, ints, floats, and Decimals."
        raise RuntimeError(msg)

    @classmethod
    def __get_validators__(cls):
        yield to_scalar


def to_scalar(v: ToScalar) -> Union[Prefixed, Literal]:
    """# Validate and convert anything in the `ToScalar` set of types to a `Prefixed` or `Literal`.
    Most importantly this handles the case in which `v` is a *string*,
    which attempts conversion to a `Prefixed`, and falls back to a `Literal` on failure."""

    if isinstance(v, (Prefixed, Literal)):
        return v  # Valid as-is, return it.

    # Now the important case: strings
    if isinstance(v, str):
        try:  # Try to convert to a Prefixed, which internally converts to a Decimal
            return Prefixed(number=v)
        except Exception:  # Catch all exceptions
            return Literal(text=v)

    # Everything else - notably including `int` and `float` - must be convertible to `Prefixed`, or fails in its validation.
    return Prefixed(number=v)


__all__ = ["Scalar", "ToScalar", "to_scalar"]
__doc__ = Scalar.__doc__
