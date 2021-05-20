import pytest
import hdl21 as h


def test_version():
    assert h.__version__ == "0.1.0"


def test_module1():
    """ Initial Module Test """

    @h.module
    class M1:
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
    @h.module
    class M1:
        s = h.Input()

    @h.module
    class M2:
        q = h.Signal()
        i = M1(s=q)

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

    M = h.Module(name="M")
    p3a = P3()
    p3b = P3(width=5)

    @h.module
    class HasGeneratorInstances:
        a = g3a(p3a)()
        b = g3b(p3b)()
        c = M()

    h.elaborate(HasGeneratorInstances)

    # FIXME: post-elab tests


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
        # Test "no Module sub-classing"

        class E(h.Module):
            ...

    with pytest.raises(RuntimeError):
        # Test "no decorating inherited types"

        @h.module
        class E2(TabError):
            ...


def test_array1():
    @h.module
    class InArray:
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

    @h.module
    class HasArray2:
        s1 = h.Signal(width=8)
        s2 = h.Signal(width=1)
        arr = h.InstArray(a, 8)(inp=s1, out=s2)

    # FIXME: some real checks here plz


def test_cycle1():
    @h.module
    class Thing:
        inp = h.Input()
        out = h.Output()

    @h.module
    class BackToBack:
        t1 = Thing()
        t2 = Thing(inp=t1.out, out=t1.inp)

    b = h.elaborate(BackToBack)

    assert isinstance(b.t1.inp, h.Signal)
    assert isinstance(b.t1.out, h.Signal)
    assert isinstance(b.t2.inp, h.Signal)
    assert isinstance(b.t2.out, h.Signal)

    # Doing the same thing in procedural code
    b2 = h.Module(name="BackToBack2")
    b2.t1 = Thing()
    b2.t2 = Thing(inp=b2.t1.out, out=b2.t1.inp)
    b2.t1(inp=b2.t2.out, out=b2.t2.inp)

    assert isinstance(b.t1.inp, h.Signal)
    assert isinstance(b.t1.out, h.Signal)
    assert isinstance(b.t2.inp, h.Signal)
    assert isinstance(b.t2.out, h.Signal)

    # FIXME: better post-elaboration checks that this works out


def test_gen3():
    import hdl21 as h

    @h.paramclass
    class MyParams:
        w = h.Param(dtype=int, desc="Input bit-width. Required")

    @h.generator
    def MyThirdGenerator(params: MyParams) -> h.Module:
        @h.module
        class Inner:
            i = h.Input(width=params.w)
            o = h.Output(width=2 * params.w)

        # Instantiate that in another Module
        @h.module
        class Outer:
            inner = Inner()

        # And manipulate that some more too
        Outer.inp = h.Input(width=params.w)
        return Outer

    h.elaborate(MyThirdGenerator, MyParams(1))


def test_prim1():
    # First test of transistor primitives
    params = h.Mos.Params()
    pmos = h.Pmos(params)
    nmos = h.Nmos(params)

    @h.module
    class HasMos:
        # Two transistors wired in parallel
        p = pmos()
        n = nmos(g=p.g, d=p.d, s=p.s, b=p.b)

    h.elaborate(HasMos)
    # FIXME: post-elab checks


def test_prim2():
    @h.module
    class HasPrims:
        p = h.Signal()
        n = h.Signal()

        _rp = h.R.Params(r=50)
        r = h.Resistor(_rp)(p=p, n=n)

        c = h.Capacitor(h.C.Params(c=1e-12))(p=p, n=n)
        l = h.Inductor(h.L.Params(l=1e-15))(p=p, n=n)
        d = h.Diode(h.D.Params())(p=p, n=n)
        s = h.Short(h.Short.Params())(p=p, n=n)

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
    m3 = h.Module(name="M3")
    m3.i1 = m1()
    m3.i2 = m2(i=m3.i1.i)
    assert "_i2_i__i1_i_" not in m3.namespace

    m3e = h.elaborate(m3)
    assert isinstance(m3e, h.Module)
    assert isinstance(m3e.i1, h.Instance)
    assert isinstance(m3e.i2, h.Instance)
    assert "_i2_i__i1_i_" in m3e.namespace


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

    @h.module
    class Host:
        # A thing with a HOST-roled interface-port
        port_ = HasRoles(port=True, role=HasRoles.Roles.HOST)

    @h.module
    class Device:
        # A thing with a DEVICE-roled interface-port
        port_ = HasRoles(port=True, role=HasRoles.Roles.DEVICE)

    @h.module
    class System:
        # Parent system-module including a host and device
        host = Host()
        dev_ = Device(port_=host.port_)

    assert isinstance(System, h.Module)
    assert isinstance(System.host, h.Instance)
    assert isinstance(System.dev_, h.Instance)
    assert "_dev__port___host_port__" not in System.namespace

    sys = h.elaborate(System)
    assert "_dev__port___host_port__" in sys.namespace


def test_proto1():
    # First Proto-export test
    import hdl21 as h
    from hdl21.proto import to_proto

    m = h.Module(name="TestProto1")
    ppkg = to_proto(m)
    assert isinstance(ppkg, h.proto.Package)
    assert len(ppkg.modules) == 1
    pm = ppkg.modules[0]
    assert isinstance(pm, h.proto.Module)
    assert pm.name.name == "TestProto1"
    assert pm.name.domain == "THIS_LIBRARYS_FLAT_NAMESPACE"
    assert len(pm.ports) == 0
    assert len(pm.instances) == 0
    assert len(pm.default_parameters) == 0


def test_proto2():
    # Proto-export test with some hierarchy
    import hdl21 as h
    from hdl21.proto import to_proto

    Child1 = h.Module(name="Child1")
    Child1.inp = h.Input(width=8)
    Child1.out = h.Output()
    Child2 = h.Module(name="Child2")
    Child2.inp = h.Input()
    Child2.out = h.Output(width=8)
    TestProto2 = h.Module(name="TestProto2")
    TestProto2.c1 = Child1()
    TestProto2.c2 = Child2()
    TestProto2.c2(inp=TestProto2.c1.out, out=TestProto2.c1.inp)

    ppkg = to_proto(TestProto2)

    assert isinstance(ppkg, h.proto.Package)
    assert len(ppkg.modules) == 3

    # Check the first Module in, Child1
    pm = ppkg.modules[0]
    assert isinstance(pm, h.proto.Module)
    assert pm.name.name == "Child1"
    assert pm.name.domain == "THIS_LIBRARYS_FLAT_NAMESPACE"
    assert len(pm.ports) == 2
    assert len(pm.instances) == 0
    assert len(pm.default_parameters) == 0

    # Check the second Module in, Child2
    pm = ppkg.modules[1]
    assert isinstance(pm, h.proto.Module)
    assert pm.name.name == "Child2"
    assert pm.name.domain == "THIS_LIBRARYS_FLAT_NAMESPACE"
    assert len(pm.ports) == 2
    assert len(pm.instances) == 0
    assert len(pm.default_parameters) == 0

    # And check the parent module
    pm = ppkg.modules[2]
    assert isinstance(pm, h.proto.Module)
    assert pm.name.name == "TestProto2"
    assert pm.name.domain == "THIS_LIBRARYS_FLAT_NAMESPACE"
    assert len(pm.ports) == 0
    assert len(pm.instances) == 2
    assert len(pm.default_parameters) == 0


def test_proto_roundtrip():
    import hdl21 as h
    from types import SimpleNamespace

    # Create an empty (named) Module
    M1 = h.Module(name="M1")

    # Protobuf round-trip it
    ppkg = h.to_proto(M1)
    ns = h.from_proto(ppkg)

    assert isinstance(ns, SimpleNamespace)
    assert isinstance(ns.M1, h.Module)
    assert len(ns.M1.signals) == 0
    assert len(ns.M1.ports) == 0
    assert len(ns.M1.instances) == 0


def test_proto_roundtrip2():
    import hdl21 as h
    from types import SimpleNamespace

    # Create a child/leaf Module
    M1 = h.Module(name="M1")
    M1.i = h.Input()
    M1.o = h.Output()
    M1.p = h.Port()

    # Create an instantiating parent-module
    M2 = h.Module(name="M2")
    M2.i = h.Input()
    M2.o = h.Output()
    M2.p = h.Port()
    M2.s = h.Signal()

    # Add a few instances of it
    M2.i0 = M1()
    M2.i1 = M1()
    M2.i2 = M1()
    M2.i0(i=M2.i, o=M2.i1.i, p=M2.p)
    M2.i1(i=M2.i0.o, o=M2.s, p=M2.p)
    M2.i2(i=M2.s, o=M2.o, p=M2.p)

    # Protobuf round-trip it
    ppkg = h.to_proto(M2)
    ns = h.from_proto(ppkg)

    # And check all kinda stuff about what comes back
    assert isinstance(ns, SimpleNamespace)
    assert isinstance(ns.M1, h.Module)
    assert isinstance(ns.M2, h.Module)

    assert len(ns.M1.signals) == 0
    assert len(ns.M1.ports) == 3
    assert "i" in ns.M1.ports
    assert ns.M1.i.direction == h.signal.PortDir.INPUT
    assert ns.M1.i.vis == h.signal.Visibility.PORT
    assert "o" in ns.M1.ports
    assert ns.M1.o.direction == h.signal.PortDir.OUTPUT
    assert ns.M1.o.vis == h.signal.Visibility.PORT
    assert "p" in ns.M1.ports
    assert ns.M1.p.direction == h.signal.PortDir.NONE
    assert ns.M1.p.vis == h.signal.Visibility.PORT
    assert len(ns.M1.instances) == 0

    assert len(ns.M2.instances) == 3
    for i in ns.M2.instances.values():
        assert i.module is ns.M1
        assert i.conns["p"] is ns.M2.p
    assert len(ns.M2.ports) == 3
    assert len(ns.M2.signals) == 2
    assert "s" in ns.M2.signals
    assert "_i1_i__i0_o_" in ns.M2.signals


def test_bigger_interfaces():
    import hdl21 as h
    from enum import Enum, auto

    class MsRoles(Enum):
        MS = auto()
        SL = auto()

    @h.interface
    class Jtag:
        roles = MsRoles
        tck = h.Signal(src=roles.MS, dest=roles.SL)
        tdi = h.Signal(src=roles.MS, dest=roles.SL)
        tms = h.Signal(src=roles.MS, dest=roles.SL)
        tdo = h.Signal(src=roles.SL, dest=roles.MS)

    @h.interface
    class Spi:
        roles = MsRoles
        sck = h.Signal(src=roles.MS, dest=roles.SL)
        cs = h.Signal(src=roles.MS, dest=roles.SL)
        dq = h.Signal(src=roles.SL, dest=roles.MS, width=4)

    @h.module
    class Chip:
        spi = Spi(role=MsRoles.MS, port=True)
        jtag = Jtag(role=MsRoles.SL, port=True)
        ...  # Actual internal content, which likely connects these down *many* levels of hierarchy

    @h.module
    class SpiFlash:
        # A typical flash memory with a SPI port
        spi = Spi(role=MsRoles.SL, port=True)

    @h.module
    class Board:
        # A typical embedded board, featuring a custom chip, SPI-connected flash, and JTAG port
        jtag = Jtag(role=MsRoles.SL)
        chip = Chip(jtag=jtag)
        flash = SpiFlash(spi=chip.spi)

    @h.module
    class Tester:
        # A typical test-widget with a JTAG port
        jtag = Jtag(role=MsRoles.MS, port=True)

    @h.module
    class TestSystem:
        # A system in which `Tester` can test `Board`
        jtag = Jtag()
        tester = Tester(jtag=jtag)
        board = Board(jtag=jtag)

    sys = h.elaborate(TestSystem)
    # FIXME: more post-elabortion tests

