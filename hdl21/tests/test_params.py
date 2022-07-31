""" 
# Hdl21 Parameters 
# Unit Tests 
"""

import pytest
from dataclasses import field, FrozenInstanceError

from pydantic import ValidationError
from pydantic.dataclasses import dataclass

# Import the PUT (package under test)
import hdl21 as h


def test_params1():
    # Initial param-class test

    @h.paramclass
    class MyParams:
        a = h.Param(dtype=int, default=5, desc="your fave")

    assert h.isparamclass(MyParams)

    m = MyParams()
    assert isinstance(m.a, int)
    assert m.a == 5
    assert isinstance(m.__params__["a"], h.Param)
    assert m.defaults() == dict(a=5)
    assert m.descriptions() == dict(a="your fave")


def test_params2():
    @h.paramclass
    class Pc2:
        # Required
        r = h.Param(dtype=str, desc="required")
        # Optional
        o = h.Param(dtype=str, default="hmmm", desc="optional")

    assert h.isparamclass(Pc2)
    assert Pc2.defaults() == dict(o="hmmm")
    assert Pc2.descriptions() == dict(r="required", o="optional")

    p = Pc2(r="provided")
    assert isinstance(p.r, str)
    assert p.r == "provided"
    assert isinstance(p.o, str)
    assert p.o == "hmmm"
    assert p.defaults() == dict(o="hmmm")
    assert p.descriptions() == dict(r="required", o="optional")


def test_params3():
    # Test parameters with a creation-time list-tuple conversion
    @h.paramclass
    class HasTuple:
        t = h.Param(dtype=tuple, desc="Go ahead, try a list")

    ht = HasTuple(t=[1, 2, 3])
    assert isinstance(ht.t, tuple)
    assert ht.t == (1, 2, 3)


def test_params4():
    # Test some param-class nesting
    from dataclasses import asdict

    @h.paramclass
    class Inner:
        i = h.Param(dtype=int, desc="Inner int-field")

    @h.paramclass
    class Outer:
        inner = h.Param(dtype=Inner, desc="Inner fields")
        f = h.Param(dtype=float, desc="A float", default=3.14159)

    o = Outer(inner=Inner(11))
    assert isinstance(o, Outer)
    assert isinstance(o.inner, Inner)
    assert o.inner == Inner(11)
    assert o.inner.i == 11
    assert o.f == 3.14159

    # Create from a (nested) dictionary
    d1 = {"inner": {"i": 11}, "f": 22.2}
    o1 = Outer(**d1)
    uname1 = h.params._unique_name(o1)
    # Convert back to another dictionary
    d2 = asdict(o1)
    # And check they line up
    assert d1 == d2
    # Round-trip back to an `Outer`
    o2 = Outer(**d2)
    uname2 = h.params._unique_name(o2)
    assert uname1 == uname2
    assert uname1 == "3dcc309796996b3a8a61db66631c5a93"


def test_bad_params1():
    # Test a handful of errors Params and paramclasses should raise.

    with pytest.raises(RuntimeError):
        # Test that creating a h.paramclass with parent-class(es) fails

        @h.paramclass
        class C(TabError):  # Of course this is a sub-class of the best built-in class
            ...

    @h.paramclass
    class C:
        a = h.Param(dtype=int, desc="Gonna Fail!")

    with pytest.raises(RuntimeError):
        # Test that sub-classing a h.paramclass fails

        class D(C):
            ...

    with pytest.raises(TypeError):
        # Test that missing arguments fail
        c = C()

    with pytest.raises(ValidationError):
        # Test invalid argument types fail

        c = C(a=TabError)

    with pytest.raises(FrozenInstanceError):
        # Test that attempts at mutating h.paramclasses fail
        c = C(a=3)
        c.a = 4

    with pytest.raises(RuntimeError):
        # Test "no Module sub-classing"

        class E(h.Module):
            ...

    with pytest.raises(RuntimeError):
        # Test "no decorating inherited types"

        @h.module
        class E2(TabError):
            ...

    with pytest.raises(RuntimeError):
        # Test bad parameter names

        @h.paramclass
        class P:
            descriptions = h.Param(dtype=str, desc="", default="BAD!")

    with pytest.raises(RuntimeError):
        # Test bad parameter names

        @h.paramclass
        class P:
            defaults = h.Param(dtype=str, desc="", default="BAD!")

    with pytest.raises(RuntimeError):
        # Test non-params in `@paramclass`

        @h.paramclass
        class P:
            something = 11

    with pytest.raises(RuntimeError):
        # Test a bad argument type
        h.params._unique_name(33)


@pytest.mark.xfail(reason="#30 https://github.com/dan-fritchman/Hdl21/issues/30")
def test_param_default_factory():
    """Test the `default_factory` feature of `Param`"""

    # Test the pydantic versions without `paramclass` first

    @dataclass
    class NoFactory:
        i: int = 11

    @dataclass
    class HasFactory:
        a: int = field(default_factory=lambda: 5)
        l: list = field(default_factory=list)
        no: NoFactory = field(default_factory=NoFactory)

    has = HasFactory()

    assert has.a == 5
    assert has.l == []
    assert has.no == NoFactory(i=11)

    # And test `paramclass`es

    @h.paramclass
    class NoFactory:
        i = h.Param(dtype=int, desc="i", default=11)

    @h.paramclass
    class HasFactory:
        a = h.Param(dtype=int, desc="a", default_factory=lambda: 5)
        l = h.Param(dtype=list, desc="l", default_factory=list)
        no = h.Param(dtype=NoFactory, desc="no", default_factory=NoFactory)

    has = HasFactory()

    assert has.a == 5
    assert has.l == []
    assert has.no == NoFactory(i=11)
