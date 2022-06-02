import hdl21 as h
from decimal import Decimal


def test_decimal():
    """ This isnt a test of Hdl21 so much as a demo and reminder of how 
    the standard library's `Decimal` works, particularly in conjunction with 
    our widely-used `pydantic.dataclasses`. 

    In short: `pydantic` converts `Decimal` valued fields to strings before
    passing them to the `Decimal` constructor. 
    https://pydantic-docs.helpmanual.io/usage/types/ """

    # Decimal-only
    assert Decimal(11) == Decimal(11)
    assert Decimal(11.1) == Decimal(11.1)
    assert Decimal("11.1") == Decimal("11.1")
    # Note these are *not* equal, due to floating-point precision
    assert Decimal(11.1) != Decimal("11.1")

    # Create a dataclass with a `Decimal` field
    from pydantic.dataclasses import dataclass

    @dataclass
    class HasDecimal:
        d: Decimal

    assert HasDecimal(11).d == Decimal(11)
    assert HasDecimal("11.1").d == Decimal("11.1")
    # These last two are the trick.
    assert HasDecimal(11.1).d == Decimal("11.1")
    assert HasDecimal(11.1).d != Decimal(11.1)


def test_prefix_numbers():
    """ Check that we get the numeric types we expect in each `Prefixed` """

    x = h.Prefixed(11, h.Prefix.FEMTO)
    assert isinstance(x.number, Decimal)
    assert x.number == 11

    x = h.Prefixed(11.1, h.Prefix.FEMTO)
    assert isinstance(x.number, Decimal)
    assert x.number == Decimal("11.1")

    x = h.Prefixed(Decimal("11.11"), h.Prefix.FEMTO)
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
    """ Test creating `Prefix` from an integer exponent. """

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
    assert h.Prefix.from_exp(0) is None
    assert h.Prefix.from_exp(-100) is None
    assert h.Prefix.from_exp(+100) is None


def test_prefix_mul():
    """ Test `Prefix` multiplication. """
    from hdl21.prefix import µ

    assert 5 * µ == 5 * h.Prefix.MICRO
    assert 5 * µ == h.Prefixed(5, h.Prefix.MICRO)


def test_e():
    """ Test the `e` shorthand notation for exponential creation """
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
    """ Test multiplying by the `e` function results, e.g. `11 * e(-9) """
    from hdl21.prefix import e

    assert 11 * e(-9) == h.Prefixed(11, h.Prefix.NANO)


def test_prefix_scaling():
    """ Test cases of `Prefixed` multiplication which do not land on other `Prefix`es, and require scaling """
    from hdl21.prefix import e

    # 1e-11, scaled to 10e-12
    assert 1 * e(-9) * h.Prefix.CENTI == 10 * e(-12)

    # 5e4, scaled to 50e3
    assert 5 * e(6) * h.Prefix.CENTI == 50 * e(3)

    # 11.11e14, scaled to 1111e12
    assert 11.11 * e(15) * h.Prefix.DECI == 1111 * e(12)
