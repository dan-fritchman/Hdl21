import pytest
from decimal import Decimal
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

import hdl21 as h


def test_decimal():
    """This isnt a test of Hdl21 so much as a demo and reminder of how
    the standard library's `Decimal` works, particularly in conjunction with
    our widely-used `pydantic.dataclasses`.

    In short: `pydantic` converts `Decimal` valued fields to strings before
    passing them to the `Decimal` constructor.
    https://pydantic-docs.helpmanual.io/usage/types/"""

    # Decimal-only
    assert Decimal(11) == Decimal(11)
    assert Decimal(11.1) == Decimal(11.1)
    assert Decimal("11.1") == Decimal("11.1")
    # Note these are *not* equal, due to floating-point precision
    assert Decimal(11.1) != Decimal("11.1")

    # Create a dataclass with a `Decimal` field
    @dataclass
    class HasDecimal:
        d: Decimal

    assert HasDecimal(11).d == Decimal(11)
    assert HasDecimal("11.1").d == Decimal("11.1")
    # These last two are the trick.
    assert HasDecimal(11.1).d == Decimal("11.1")
    assert HasDecimal(11.1).d != Decimal(11.1)


def test_prefix_numbers():
    """Check that we get the numeric types we expect in each `Prefixed`"""

    x = h.Prefixed(number=11, prefix=h.Prefix.FEMTO)
    assert isinstance(x.number, Decimal)
    assert x.number == 11

    x = h.Prefixed(number=11.1, prefix=h.Prefix.FEMTO)
    assert isinstance(x.number, Decimal)
    assert x.number == Decimal("11.1")

    x = h.Prefixed(number=Decimal("11.11"), prefix=h.Prefix.FEMTO)
    assert isinstance(x.number, Decimal)
    assert x.number == Decimal("11.11")


def test_prefix_shortname():
    assert h.prefix.f == h.Prefix.FEMTO
    assert h.prefix.p == h.Prefix.PICO
    assert h.prefix.n == h.Prefix.NANO
    assert h.prefix.µ == h.Prefix.MICRO
    assert h.prefix.m == h.Prefix.MILLI
    assert h.prefix.K == h.Prefix.KILO
    assert h.prefix.M == h.Prefix.MEGA
    assert h.prefix.G == h.Prefix.GIGA
    assert h.prefix.T == h.Prefix.TERA
    assert h.prefix.P == h.Prefix.PETA


def test_prefix_from_exp():
    """Test creating `Prefix` from an integer exponent."""

    assert h.Prefix.from_exp(-24) == h.Prefix.YOCTO
    assert h.Prefix.from_exp(-21) == h.Prefix.ZEPTO
    assert h.Prefix.from_exp(-18) == h.Prefix.ATTO
    assert h.Prefix.from_exp(-15) == h.Prefix.FEMTO
    assert h.Prefix.from_exp(-12) == h.Prefix.PICO
    assert h.Prefix.from_exp(-9) == h.Prefix.NANO
    assert h.Prefix.from_exp(-6) == h.Prefix.MICRO
    assert h.Prefix.from_exp(-3) == h.Prefix.MILLI
    assert h.Prefix.from_exp(-2) == h.Prefix.CENTI
    assert h.Prefix.from_exp(-1) == h.Prefix.DECI
    assert h.Prefix.from_exp(0) == h.Prefix.UNIT
    assert h.Prefix.from_exp(1) == h.Prefix.DECA
    assert h.Prefix.from_exp(2) == h.Prefix.HECTO
    assert h.Prefix.from_exp(3) == h.Prefix.KILO
    assert h.Prefix.from_exp(6) == h.Prefix.MEGA
    assert h.Prefix.from_exp(9) == h.Prefix.GIGA
    assert h.Prefix.from_exp(12) == h.Prefix.TERA
    assert h.Prefix.from_exp(15) == h.Prefix.PETA
    assert h.Prefix.from_exp(18) == h.Prefix.EXA
    assert h.Prefix.from_exp(21) == h.Prefix.ZETTA
    assert h.Prefix.from_exp(24) == h.Prefix.YOTTA

    # Check a few unsupported values
    assert h.Prefix.from_exp(-100) is None
    assert h.Prefix.from_exp(+100) is None


def test_prefix_mul():
    """Test `Prefix` multiplication."""
    from hdl21.prefix import µ

    assert 5 * µ == 5 * h.Prefix.MICRO
    assert 5 * µ == h.Prefixed(number=5, prefix=h.Prefix.MICRO)


def test_e():
    """Test the `e` shorthand notation for exponential creation"""
    from hdl21.prefix import e

    assert e(-24) == h.Prefix.YOCTO
    assert e(-21) == h.Prefix.ZEPTO
    assert e(-18) == h.Prefix.ATTO
    assert e(-15) == h.Prefix.FEMTO
    assert e(-12) == h.Prefix.PICO
    assert e(-9) == h.Prefix.NANO
    assert e(-6) == h.Prefix.MICRO
    assert e(-3) == h.Prefix.MILLI
    assert e(-2) == h.Prefix.CENTI
    assert e(-1) == h.Prefix.DECI
    assert e(1) == h.Prefix.DECA
    assert e(2) == h.Prefix.HECTO
    assert e(3) == h.Prefix.KILO
    assert e(6) == h.Prefix.MEGA
    assert e(9) == h.Prefix.GIGA
    assert e(12) == h.Prefix.TERA
    assert e(15) == h.Prefix.PETA
    assert e(18) == h.Prefix.EXA
    assert e(21) == h.Prefix.ZETTA
    assert e(24) == h.Prefix.YOTTA


def test_e_mult():
    """Test multiplying by the `e` function results, e.g. `11 * e(-9)"""
    from hdl21.prefix import e

    assert 11 * e(-9) == h.Prefixed(number=11, prefix=h.Prefix.NANO)


def test_prefix_scaling():
    """Test cases of `Prefixed` multiplication which do not land on other `Prefix`es, and require scaling"""
    from hdl21.prefix import e

    # 1e-11, scaled to 10e-12
    assert 1 * e(-9) * h.Prefix.CENTI == 10 * e(-12)

    # 5e4, scaled to 50e3
    assert 5 * e(6) * h.Prefix.CENTI == 50 * e(3)

    # 11.11e14, scaled to 1111e12
    assert 11.11 * e(15) * h.Prefix.DECI == 1111 * e(12)


def test_prefix_conversion():
    """Test types that can be converted to `Prefixed`'s internal `Decimal`."""

    h.Prefixed(number="11.11", prefix=h.Prefix.YOCTO)
    h.Prefixed(number=11.11, prefix=h.Prefix.YOCTO)
    h.Prefixed(number=11, prefix=h.Prefix.YOCTO)


def test_unit_prefix():
    """Test the UNIT prefix"""
    assert h.Prefixed(number=11) == h.Prefixed(number=11, prefix=h.Prefix.UNIT)
    assert h.Prefixed(number="11") == h.Prefixed(number=11)
    assert h.Prefixed(number="11") == h.Prefixed(number=11.0)


def test_prefixed_and_scalar_conversions():
    """Test inline conversions of built-in numeric types to `Prefixed` and `Scalar`."""

    @dataclass
    class P:
        x: h.Prefixed
        y: h.Scalar

    # Test with int for each
    p = P(x=1, y=1)
    assert p.x == h.Prefixed(number=Decimal(1))
    assert p.y.inner == h.Prefixed(number=Decimal(1))

    # Test with float for each
    p = P(x=3.0, y=3.0)
    assert p.x == h.Prefixed(number=Decimal(3.0))
    assert p.y.inner == h.Prefixed(number=Decimal(3.0))

    # Test with str for each
    p = P(x="2e-9", y="2e-9")
    assert p.x == h.Prefixed(number=Decimal("2e-9"))
    assert p.y.inner == h.Prefixed(number=Decimal("2e-9"))

    # Test with an expression-literal for the `Scalar`
    p = P(x=11.11, y="m*x+b")
    assert p.x == h.Prefixed(number=Decimal(11.11))
    assert p.y.inner == h.Literal(txt="m*x+b")

    # Test some invalid types
    with pytest.raises(ValidationError):
        p = P(x=None, y=2)
    with pytest.raises(ValidationError):
        p = P(x=3, y=None)
