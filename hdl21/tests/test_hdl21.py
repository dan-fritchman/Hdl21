import pytest
import hdl21 as h


def test_version():
    assert h.__version__ == "0.1.0"
    

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
        w = h.Param(dtype=int, desc="five", default=5)

    @h.generator
    def gen1(params: MyParams) -> h.Module:
        m = h.Module()
        m.i = h.Input(width=params.w)
        return m

    m = h.elaborate(gen1, MyParams(w=3))

    assert m.name == "gen1"
    assert isinstance(m.i, h.Signal)
    assert m._genparams == MyParams(w=3)


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


def test_params3():
    # Test some list-tuple conversion
    import hdl21 as h

    @h.paramclass
    class HasTuple:
        t = h.Param(dtype=tuple, desc="Go ahead, try a list")

    h = HasTuple(t=[1, 2, 3])
    assert isinstance(h.t, tuple)
    assert h.t == (1, 2, 3)


def test_params4():
    # Test some param-class nesting
    import hdl21 as h

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

    from dataclasses import asdict

    # Create from a (nested) dictionary
    d1 = {"inner": {"i": 11}, "f": 22.2}
    o = Outer(**d1)
    # Convert back to another dictionary
    d2 = asdict(o)
    # And check they line up
    assert d1 == d2


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

    with pytest.raises(RuntimeError):
        # Test the "no setattrs allowed" in class-def

        class E(h.Module):
            a = h.Signal()
            a.b = 6

    with pytest.raises(RuntimeError):
        # And test this on literal values

        class E2(h.Module):
            a = 3
            a.b = 6


def test_array1():
    class InArray(h.Module):
        inp = h.Input()
        out = h.Output()

    m = h.Module(name="HasArray")
    m.s1 = h.Signal(width=8)
    m.s2 = h.Signal(width=1)
    m.arr = h.InstArray(InArray, 8)
    m.arr.inp = m.s1
    m.arr.out = m.s2

    assert m.name == "HasArray"


def test_array2():
    a = h.Module(name="a")

    class HasArray2(h.Module):
        s1 = h.Signal(width=8)
        s2 = h.Signal(width=1)
        arr = h.InstArray(a, 8)(inp=s1, out=s2)


def test_cycle1():
    class Thing(h.Module):
        inp = h.Input()
        out = h.Output()

    class BackToBack(h.Module):
        t1 = h.Instance(Thing)
        t2 = h.Instance(Thing)(inp=t1.out, out=t1.inp)

    b = h.elaborate(BackToBack)

    assert isinstance(b.t1.inp, h.PortRef)
    assert isinstance(b.t1.out, h.PortRef)
    assert isinstance(b.t2.inp, h.PortRef)
    assert isinstance(b.t2.out, h.PortRef)

    # Doing the same thing in procedural code
    b2 = h.Module(name="BackToBack2")
    b2.t1 = h.Instance(Thing)
    b2.t2 = h.Instance(Thing)(inp=b2.t1.out, out=b2.t1.inp)
    b2.t1(inp=b2.t2.out, out=b2.t2.inp)

    assert isinstance(b.t1.inp, h.PortRef)
    assert isinstance(b.t1.out, h.PortRef)
    assert isinstance(b.t2.inp, h.PortRef)
    assert isinstance(b.t2.out, h.PortRef)

    # FIXME: better post-elaboration checks that this works out


def test_gen3():
    import hdl21 as h

    @h.paramclass
    class MyParams:
        w = h.Param(dtype=int, desc="Input bit-width. Required")

    @h.generator
    def MyThirdGenerator(params: MyParams) -> h.Module:
        # Create an internal Module
        class Inner(h.Module):
            i = h.Input(width=params.w)

        # Manipulate it a bit
        o = h.Output(width=2 * Inner.i.width)

        # FIXME! Versions like this don't work; decide what to do with em.
        with pytest.raises(TypeError):

            class Inner2(h.Module):
                i = h.Input(width=params.w)
                o = h.Output(width=2 * params.w)

        # Instantiate that in another Module
        class Outer(h.Module):
            inner = h.Instance(Inner)

        # And manipulate that some more too
        Outer.inp = h.Input(width=params.w)
        return Outer

    h.elaborate(MyThirdGenerator, MyParams(1))


def test_prim1():
    # First test of transistor primitives
    params = h.Mos.Params()
    pmos = h.Pmos(params)
    nmos = h.Nmos(params)

    class HasMos(h.Module):
        # Two transistors wired in parallel
        p = h.Instance(pmos)(g=n.g, d=n.d, s=n.s, b=n.b)
        n = h.Instance(nmos)(g=p.g, d=p.d, s=p.s, b=p.b)

    h.elaborate(HasMos)


def test_prim2():
    class HasPrims(h.Module):
        p = h.Signal()
        n = h.Signal()

        _rp = h.R.Params(r=50)
        r = h.Instance(h.Resistor(_rp))(p=p, n=n)

        c = h.Instance(h.Capacitor(h.C.Params(c=1e-12)))(p=p, n=n)
        l = h.Instance(h.Inductor(h.L.Params(l=1e-15)))(p=p, n=n)
        d = h.Instance(h.Diode(h.D.Params()))(p=p, n=n)
        s = h.Instance(h.Short(h.Short.Params()))(p=p, n=n)

    h.elaborate(HasPrims)


def test_intf1():
    # Create an interface

    import hdl21 as h

    i1 = h.Interface(name="MyFirstInterface")
    i1.s1 = h.Signal()
    i1.s2 = h.Signal()

    assert isinstance(i1, h.Interface)
    assert isinstance(i1.s1, h.Signal)
    assert isinstance(i1.s2, h.Signal)

    ii1 = i1()
    assert isinstance(ii1, h.InterfaceInstance)
    assert ii1.role is None
    assert ii1.port == False


def test_intf2():
    # Wire up a few Modules via interfaces
    import hdl21 as h

    MySecondInterface = h.Interface(name="MySecondInterface")

    m1 = h.Module(name="M1")
    m1.i = MySecondInterface(port=True)
    m2 = h.Module(name="M2")
    m2.i = MySecondInterface(port=True)

    # Now create a parent Module connecting the two
    m3 = h.Module()
    m3.i1 = h.Instance(m1)
    m3.i2 = h.Instance(m2)(i=m1.i)


def test_inft3():
    # Test the interface-definition decorator

    import hdl21 as h

    @h.interface
    class Diff:  # Differential Signal Interface
        p = h.Signal()
        n = h.Signal()

    @h.interface
    class DisplayPort:  # DisplayPort, kinda
        main_link = Diff()
        aux = h.Signal()

    assert isinstance(DisplayPort, h.Interface)
    assert isinstance(DisplayPort(), h.InterfaceInstance)
    assert isinstance(DisplayPort.main_link, h.InterfaceInstance)
    assert isinstance(DisplayPort.main_link.p, h.PortRef)
    assert isinstance(DisplayPort.main_link.n, h.PortRef)
    assert isinstance(DisplayPort.aux, h.Signal)
    assert isinstance(Diff, h.Interface)
    assert isinstance(Diff(), h.InterfaceInstance)
    assert isinstance(Diff.p, h.Signal)

    assert isinstance(Diff.n, h.Signal)


def test_intf4():
    # Test interface roles
    import hdl21 as h
    from enum import Enum, EnumMeta, auto

    @h.interface
    class Diff:  # Differential Signal Interface
        p = h.Signal()
        n = h.Signal()

    @h.interface
    class HasRoles:  # An Interface with Roles
        class Roles(Enum):  # USB-Style Role Nomenclature
            HOST = auto()
            DEVICE = auto()

        # Create signals going in either direction
        tx = h.Signal(src=Roles.HOST, dest=Roles.DEVICE)
        rx = h.Signal(src=Roles.DEVICE, dest=Roles.HOST)

        # And create differential versions thereof
        txd = Diff(src=Roles.HOST, dest=Roles.DEVICE)
        rxd = Diff(src=Roles.DEVICE, dest=Roles.HOST)

    hr = HasRoles()
    assert isinstance(HasRoles, h.Interface)
    assert isinstance(HasRoles.roles, EnumMeta)
    assert isinstance(HasRoles.Roles, EnumMeta)
    assert isinstance(hr, h.InterfaceInstance)
    assert isinstance(HasRoles.tx, h.Signal)
    assert isinstance(HasRoles.rx, h.Signal)
    assert isinstance(HasRoles.txd, h.InterfaceInstance)
    assert isinstance(HasRoles.rxd, h.InterfaceInstance)

    class Host(h.Module):
        # A thing with a HOST-roled interface-port
        port_ = HasRoles(port=True, role=HasRoles.Roles.HOST)

    class Device(h.Module):
        # A thing with a DEVICE-roled interface-port
        port_ = HasRoles(port=True, role=HasRoles.Roles.DEVICE)

    class System(h.Module):
        # Parent system-module including a host and device
        host = h.Instance(Host)
        dev_ = h.Instance(Device)(port_=host.port_)

    assert isinstance(System, h.Module)
    assert isinstance(System.host, h.Instance)
    assert isinstance(System.dev_, h.Instance)

    h.elaborate(System)
    # FIXME: better post-elab checks

