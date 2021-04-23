import pytest
import hdl21 as h


def test_health():
    """ Test the core library is "there". 
    Also check whether the module-system's version """
    from .. import health as health1
    from hdl21 import health as health2

    a = health1()
    assert a == "alive"

    if health1 is not health2:
        import warnings
        import hdl21

        warnings.warn(f"Module under test is not installed version {hdl21}")


def test_module1():
    """ Initial Module Test """

    class M1(h.Module):
        a = h.Input()
        b = h.Output()
        c = h.Inout()
        d = h.Port()
        e = h.Signal()
        f = h.Signal()

    assert isinstance(M1, h.Module)
    assert isinstance(M1.ports, dict)
    assert isinstance(M1.signals, dict)
    assert isinstance(M1.instances, dict)
    assert "a" in M1.ports
    assert "a" not in M1.signals
    assert "b" in M1.ports
    assert "b" not in M1.signals
    assert "c" in M1.ports
    assert "c" not in M1.signals
    assert "d" in M1.ports
    assert "d" not in M1.signals
    assert "e" in M1.signals
    assert "e" not in M1.ports
    assert "f" in M1.signals
    assert "f" not in M1.ports
    assert M1.e is not M1.f


def test_module2():
    class M1(h.Module):
        s = h.Input()

    class M2(h.Module):
        i = h.Instance(M1)(s=q)
        q = h.Signal()

    assert isinstance(M1, h.Module)
    assert isinstance(M2, h.Module)
    assert isinstance(M1.ports["s"], h.Signal)
    assert isinstance(M2.signals["q"], h.Signal)
    assert isinstance(M2.instances["i"], h.Instance)

    # Test the getattr magic for signals, ports, and instances
    assert isinstance(M2.i, h.Instance)
    assert M2.instances["i"] is M2.i
    assert isinstance(M2.q, h.Signal)
    assert M2.signals["q"] is M2.q
    assert isinstance(M1.s, h.Signal)
    assert M1.ports["s"] is M1.s


def test_generator1():
    @h.paramclass
    class MyParams:
        a = h.Param(dtype=int, desc="five", default=5)

    @h.generator
    def gen1(params: MyParams) -> h.Module:
        m = h.Module()
        m.i = h.Input()
        return m

    m = h.elaborate(gen1, MyParams(a=3))

    assert m.name == "gen1"
    assert isinstance(m.i, h.Signal)
    assert m._genparams == MyParams(a=3)


def test_generator2():
    @h.paramclass
    class P2:
        f = h.Param(dtype=float, desc="a real number", default=1e-11)

    @h.generator
    def g2(params: P2, ctx: h.Context) -> h.Module:
        assert isinstance(params, P2)
        assert isinstance(ctx, h.Context)
        return h.Module()

    m = h.elaborate(g2, P2())

    assert isinstance(m, h.Module)
    assert m.name == "g2"
    assert m._genparams == P2()


def test_generator3():
    @h.paramclass
    class P3:
        width = h.Param(dtype=int, desc="bit-width, maybe", default=1)

    @h.generator
    def g3a(params: P3) -> h.Module:
        return h.Module()

    @h.generator
    def g3b(params: P3, ctx: h.Context) -> h.Module:
        return h.Module()

    m = h.Module(name="m")

    class HasGeneratorInstances(h.Module):
        a = h.Instance(g3a, P3())
        b = h.Instance(g3b, P3(width=5))
        c = h.Instance(m)

    h.elaborate(HasGeneratorInstances)


def test_params1():
    from hdl21 import paramclass, Param, isparamclass

    @paramclass
    class MyParams:
        a = Param(dtype=int, default=5, desc="your fave")

    assert isparamclass(MyParams)

    m = MyParams()
    assert isinstance(m.a, int)
    assert m.a == 5
    assert isinstance(m.__params__["a"], Param)
    assert m.defaults() == dict(a=5)
    assert m.descriptions() == dict(a="your fave")


def test_params2():
    from hdl21 import paramclass, Param, isparamclass

    @paramclass
    class Pc2:
        # Required
        r = Param(dtype=str, desc="required")
        # Optional
        o = Param(dtype=str, default="hmmm", desc="optional")

    assert isparamclass(Pc2)
    assert Pc2.defaults() == dict(o="hmmm")
    assert Pc2.descriptions() == dict(r="required", o="optional")

    p = Pc2(r="provided")
    assert isinstance(p.r, str)
    assert p.r == "provided"
    assert isinstance(p.o, str)
    assert p.o == "hmmm"
    assert p.defaults() == dict(o="hmmm")
    assert p.descriptions() == dict(r="required", o="optional")


def test_bad_params1():
    # Test a handful of errors Params and paramclasses should raise.

    from hdl21 import (
        paramclass,
        Param,
        isparamclass,
        ValidationError,
        FrozenInstanceError,
    )

    with pytest.raises(RuntimeError):
        # Test that creating a paramclass with parent-class(es) fails

        @paramclass
        class C(TabError):  # Of course this is a sub-class of the best built-in class
            ...

    @paramclass
    class C:
        a = Param(dtype=int, desc="Gonna Fail!")

    with pytest.raises(RuntimeError):
        # Test that sub-classing a paramclass fails

        class D(C):
            ...

    with pytest.raises(TypeError):
        # Test that missing arguments fail
        c = C()

    with pytest.raises(ValidationError):
        # Test invalid argument types fail

        c = C(a=TabError)

    with pytest.raises(FrozenInstanceError):
        # Test that attempts at mutating paramclasses fail
        c = C(a=3)
        c.a = 4
