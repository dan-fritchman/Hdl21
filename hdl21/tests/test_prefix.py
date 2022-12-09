import hdl21 as h
from decimal import Decimal


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
    """Check that we get the numeric types we expect in each `Prefixed`"""

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
    assert h.prefix.y == h.Prefix.YOCTO
    assert h.prefix.z == h.Prefix.ZEPTO
    assert h.prefix.a == h.Prefix.ATTO
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
    assert h.prefix.E == h.Prefix.EXA
    assert h.prefix.Z == h.Prefix.ZETTA
    assert h.prefix.Y == h.Prefix.YOTTA

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

def test_prefix_mul():
    """Test `Prefix` multiplication."""
    from hdl21.prefix import µ, M, e

    assert 5 * µ == 5 * h.Prefix.MICRO
    assert 5 * µ == h.Prefixed(5, h.Prefix.MICRO)
    assert µ * M == e(0)
    

def test_prefix_div():
    """Test `Prefix` division"""
    from hdl21.prefix import µ, M, e

    assert M / µ == e(12)
    assert µ / M == e(-12)


def test_prefix_pow():
    """Test `Prefix` exponentiation"""
    from hdl21.prefix import µ, e

    assert µ ** 2 == e(-12)
    assert µ ** 0.5 == e(-3)
    assert µ ** -1 == e(6)

def test_e():
    """Test the `e` shorthand notation for exponential creation"""
    from hdl21.prefix import e

    assert e(-24).symbol == h.Prefix.YOCTO
    assert e(-21).symbol == h.Prefix.ZEPTO
    assert e(-18).symbol == h.Prefix.ATTO
    assert e(-15).symbol == h.Prefix.FEMTO
    assert e(-12).symbol == h.Prefix.PICO
    assert e(-9).symbol == h.Prefix.NANO
    assert e(-6).symbol == h.Prefix.MICRO
    assert e(-3).symbol == h.Prefix.MILLI
    assert e(-2).symbol == h.Prefix.CENTI
    assert e(-1).symbol == h.Prefix.DECI
    assert e(1).symbol == h.Prefix.DECA
    assert e(2).symbol == h.Prefix.HECTO
    assert e(3).symbol == h.Prefix.KILO
    assert e(6).symbol == h.Prefix.MEGA
    assert e(9).symbol == h.Prefix.GIGA
    assert e(12).symbol == h.Prefix.TERA
    assert e(15).symbol == h.Prefix.PETA
    assert e(18).symbol == h.Prefix.EXA
    assert e(21).symbol == h.Prefix.ZETTA
    assert e(24).symbol == h.Prefix.YOTTA


def test_e_mult():
    """Test multiplying by the `e` function results, e.g. `11 * e(-9)"""
    from hdl21.prefix import e, _epsilon_equiv

    assert 11 * e(-9) == h.Prefixed(11, h.Prefix.NANO)
    assert 11 * e(1.5) * e(4.5) == 11 * e(6)
    assert 11 * e(0.123) * e(0.123) * e(0.123) == 11 * e(0.369)
    assert 11 * e(1) * e(-1) == 11 * e(0)
    assert 11 * e(1) * e(-2) * e(3) == 11 * e(2)
    assert 1 * e(0.123) * e(-0.123) == 1 * e(0)
    assert 1 * e(-0.5) * e(1) == 1 * e(0.5)

    # Good enough tests
    assert _epsilon_equiv(1 * e(-3) * e(3.3), 1 * e(0.3), 10)
    assert _epsilon_equiv(1 * e(-0.75) * e(0.5), 1 * e (-0.25), 25)
    assert _epsilon_equiv(1 * e(-0.123) * e(0.003) * e(0.1), 1 * e(-0.02), 25)

def test_e_pow():
    """Test raising Prefixed numbers to powers"""
    from hdl21.prefix import e, _epsilon_equiv

    assert (1 * e(1)) ** 2 == 1 * e(2)
    assert (2 * e(-2)) ** 2 == 4 * e(-4)

    # Good enough tests
    assert _epsilon_equiv((3 * e(4)) ** 0.25,Decimal(3**0.25)*e(1),15)

def test_e_div():
    """Test dividing Prefixed numbers by numbers"""
    from hdl21.prefix import e,_epsilon_equiv

    assert e(3)/e(2) == e(1)
    assert (1*e(3))/(1*e(2)) == 1 * e(1)

    # Test scalar division
    assert (1*e(2))/2  == 0.5 * e(2) == 5 * e(1)

    # Good enough tests
    assert _epsilon_equiv((-1*e(-2))/(-1*e(-2.3)), 1 * e(0.3), 10)
    assert _epsilon_equiv((2*e(2.9))/(4*e(0.4)),0.5*e(2.5),10)

def test_prefix_scaling():
    """Test cases of `Prefixed` multiplication which do not land on other `Prefix`es, and require scaling"""
    from hdl21.prefix import e, _epsilon_equiv

    # Explicit scaling
    assert _epsilon_equiv((Decimal(11.11) * e(2)).scale(e(0).symbol),Decimal(1111) * e(0), 12)
    assert _epsilon_equiv((Decimal(1.11) * e(-1)).scale(e(-3).symbol), Decimal(111) * e(-3), 12)
    assert _epsilon_equiv((Decimal(111) * e(0)).scale(e(3).symbol), Decimal(0.111) * e(3), 12)

    # Inline Scaling
    assert _epsilon_equiv(Decimal(11.11) * e(2) * e(0), Decimal(1111) * e(0), 12)
    assert _epsilon_equiv(1.11 * e(-2) * e(-3), 11.1 * e(-6), 12)
    assert _epsilon_equiv(111 * e(3) * e(3), 0.111 * e(9), 12)

    # Automatic Scaling
    assert _epsilon_equiv((1000 * e(0)).scale(), 1 * e(3),12)
    assert _epsilon_equiv((0.001 * e(0)).scale(), 1 * e(-3),12)
    assert _epsilon_equiv((1000 * e(3)).scale(), 1 * e(6),12)

def test_prefix_comparison():
    """Test cases of `Prefixed` comparison operators"""
    from hdl21.prefix import e

    # Less than
    assert 1 * e(0) < 2 * e(0)
    assert 1 * e(3) < 1 * e(6)
    assert 1 * e(-6) < 1 * e(-3)

    # Less than or equal to
    assert 1 * e(0) <= 2 * e(0)
    assert 1 * e(0) <= 1 * e(0)
    assert 1 * e(3) <= 1 * e(6)
    assert 1 * e(3) <= 1 * e(3)
    assert 1 * e(-6) <= 1 * e(-3)
    assert 1 * e(-6) <= 1 * e(-6)

    # Not Equal to
    assert 1 * e(0) != 2 * e(0)
    assert 1 * e(-12) != 0.00001 * e(-5)
    assert 1 * e(6) != 10000 * e(1)

    # Greater than
    assert 2 * e(0) > 1 * e(0)
    assert 1 * e(6) > 1 * e(3)
    assert 1 * e(-3) > 1 * e(-6)

    # Greater than or equal to
    assert 2 * e(0) >= 1 * e(0)
    assert 1 * e(0) >= 1 * e(0)
    assert 1 * e(6) >= 1 * e(3)
    assert 1 * e(3) >= 1 * e(3)
    assert 1 * e(-3) >= 1 * e(-6)
    assert 1 * e(-6) >= 1 * e(-6)
   

def test_prefix_conversion():
    """Test types that can be converted to `Prefixed`'s internal `Decimal`."""

    h.Prefixed(number="11.11", prefix=h.Prefix.YOCTO)
    h.Prefixed(number=11.11, prefix=h.Prefix.YOCTO)
    h.Prefixed(number=11, prefix=h.Prefix.YOCTO)


def test_unit_prefix():
    """Test the UNIT prefix"""
    assert h.Prefixed(11) == h.Prefixed(11, h.Prefix.UNIT)
    assert h.Prefixed("11") == h.Prefixed(11)
    assert h.Prefixed("11") == h.Prefixed(11.0)
