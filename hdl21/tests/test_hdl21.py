import pytest
from io import StringIO
from types import SimpleNamespace
from enum import Enum, auto

# Import the PUT (package under test)
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

    m = h.elaborate(gen1(MyParams(w=3)))

    assert m.name == "gen1(MyParams(w=3))"
    assert isinstance(m.i, h.Signal)


def test_generator2():
    @h.paramclass
    class P2:
        f = h.Param(dtype=float, desc="a real number", default=1e-11)

    @h.generator
    def g2(params: P2, ctx: h.Context) -> h.Module:
        # Generator which takes a Context-argument
        assert isinstance(params, P2)
        assert isinstance(ctx, h.Context)
        return h.Module()

    m = h.elaborate(g2(P2()))

    assert isinstance(m, h.Module)
    assert m.name == "g2(P2(f=1e-11))"


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
    class HasGen:
        a = g3a(p3a)()
        b = g3b(p3b)()
        c = M()

    # Elaborate the top module
    h.elaborate(HasGen)

    # Post-elab checks
    assert isinstance(HasGen.a, h.Instance)
    assert isinstance(HasGen.a.of, h.GeneratorCall)
    assert HasGen.a.of.gen is g3a
    assert HasGen.a.of.arg == P3()
    assert isinstance(HasGen.a.of.result, h.Module)
    assert HasGen.a.of.result.name == "g3a(P3(width=1))"
    assert isinstance(HasGen.b, h.Instance)
    assert isinstance(HasGen.b.of, h.GeneratorCall)
    assert isinstance(HasGen.b.of.result, h.Module)
    assert HasGen.b.of.result.name == "g3b(P3(width=5))"
    assert HasGen.b.of.gen is g3b
    assert HasGen.b.of.arg == P3(width=5)
    assert isinstance(HasGen.c, h.Instance)
    assert isinstance(HasGen.c.of, h.Module)
    assert HasGen.c.of is M


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
    assert uname1 == "Outer(3dcc309796996b3a8a61db66631c5a93)"


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
    """ Basic Instance-Array Test """
    a = h.Module(name="a")
    a.inp = h.Port(width=1)
    a.out = h.Port(width=1)

    @h.module
    class HasArray2:
        s1 = h.Signal(width=8)
        s2 = h.Signal(width=1)
        arr = h.InstArray(a, 8)(inp=s1, out=s2)

    assert len(HasArray2.instances) == 0
    assert len(HasArray2.instarrays) == 1

    # Elaborate, flattening arrays along the way
    h.elaborate(HasArray2)

    # Post-elab checks
    assert len(HasArray2.instances) == 8
    assert len(HasArray2.instarrays) == 0


def test_cycle1():
    """ Test cyclical connection-graphs, i.e. a back-to-back pair of instances """

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
    b2.t2 = Thing()
    b2.t2.inp = b2.t1.out
    b2.t2.out = b2.t1.inp

    assert isinstance(b2.t1.inp, h.PortRef)
    assert isinstance(b2.t1.out, h.PortRef)
    assert isinstance(b2.t2.inp, h.PortRef)
    assert isinstance(b2.t2.out, h.PortRef)

    b2 = h.elaborate(b2)

    assert len(b2.instances) == 2
    assert len(b2.instarrays) == 0
    assert len(b2.interfaces) == 0
    assert len(b2.ports) == 0
    assert len(b2.signals) == 2
    assert "_t2_inp_t1_out_" in b2.signals
    assert "_t2_out_t1_inp_" in b2.signals


def test_gen3():
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
            i = h.Signal(width=params.w)
            o = h.Signal(width=2 * params.w)
            inner = Inner(i=i, o=o)

        # And manipulate that some more too
        Outer.inp = h.Input(width=params.w)
        return Outer

    h.elaborate(MyThirdGenerator(MyParams(1)))

    # FIXME: post-elab checks


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
    # FIXME: post-elab checks


def test_prim_proto1():
    # Test round-tripping primitives through proto

    @h.module
    class HasPrims:
        p = h.Signal()
        n = h.Signal()

        # Wire up a bunch of two-terminal primitives in parallel
        _rp = h.R.Params(r=50)
        r = h.Resistor(_rp)(p=p, n=n)
        _cp = h.C.Params(c=1e-12)
        c = h.Capacitor(_cp)(p=p, n=n)
        _lp = h.L.Params(l=1e-15)
        l = h.Inductor(_lp)(p=p, n=n)
        _dp = h.D.Params()
        d = h.Diode(_dp)(p=p, n=n)
        _sp = h.Short.Params()
        s = h.Short(_sp)(p=p, n=n)

    ppkg = h.to_proto(HasPrims)

    assert isinstance(ppkg, h.proto.Package)
    assert len(ppkg.modules) == 1
    assert ppkg.domain == ""

    # Check the proto-Module
    pm = ppkg.modules[0]
    assert isinstance(pm, h.proto.Module)
    assert pm.name == "hdl21.tests.test_hdl21.HasPrims"
    assert len(pm.ports) == 0
    assert len(pm.signals) == 2
    assert len(pm.instances) == 5
    assert len(pm.default_parameters) == 0
    for inst in pm.instances:
        assert isinstance(inst, h.proto.Instance)
        assert inst.module.WhichOneof("to") == "external"
        assert inst.module.external.domain in ["hdl21.ideal", "hdl21.primitives"]

    ns = h.from_proto(ppkg)

    assert isinstance(ns, SimpleNamespace)
    ns = ns.hdl21.tests.test_hdl21
    assert isinstance(ns, SimpleNamespace)
    assert hasattr(ns, "HasPrims")
    HasPrims = ns.HasPrims
    assert isinstance(HasPrims, h.Module)
    assert len(HasPrims.ports) == 0
    assert len(HasPrims.signals) == 2
    assert len(HasPrims.instances) == 5
    for inst in HasPrims.instances.values():
        assert isinstance(inst._resolved, h.primitives.PrimitiveCall)


def test_intf1():
    # Create an interface

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

    MySecondInterface = h.Interface(name="MySecondInterface")
    MySecondInterface.s = h.Signal()

    m1 = h.Module(name="M1")
    m1.i = MySecondInterface(port=True)
    m2 = h.Module(name="M2")
    m2.i = MySecondInterface(port=True)

    # Now create a parent Module connecting the two
    m3 = h.Module(name="M3")
    m3.i1 = m1()
    m3.i2 = m2(i=m3.i1.i)
    assert "_i2_i_i1_i_" not in m3.namespace

    # First run the "implicit interfaces" pass, and see that an explicit one is created
    from hdl21.elab import ElabPass

    m3 = h.elaborate(m3, passes=[ElabPass.IMPLICIT_INTERFACES])
    assert isinstance(m3, h.Module)
    assert isinstance(m3.i1, h.Instance)
    assert isinstance(m3.i2, h.Instance)
    assert "_i2_i_i1_i_" in m3.namespace

    # Now elaborate it the rest of the way, to scalar signals
    m3 = h.elaborate(m3)
    assert "_i2_i_i1_i_" not in m3.namespace
    assert "__i2_i_i1_i__s_" in m3.namespace
    assert isinstance(m3.get("__i2_i_i1_i__s_"), h.Signal)
    assert m3.get("__i2_i_i1_i__s_") in m3.i1.conns.values()


def test_intf3():
    # Test the interface-definition decorator

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
    assert "_dev__port__host_port__" not in System.namespace

    # First run the "implicit interfaces" pass, and see that an explicit one is created
    from hdl21.elab import ElabPass

    sys = h.elaborate(System, passes=[ElabPass.IMPLICIT_INTERFACES])
    assert "_dev__port__host_port__" in sys.namespace

    # Now expand the rest of the way, down to scalar signals
    # Check that interface went away, and its constituent signals replaced it
    sys = h.elaborate(sys)
    assert "_dev__port__host_port__" not in sys.namespace
    assert "__dev__port__host_port___tx_" in sys.namespace
    assert "__dev__port__host_port___rx_" in sys.namespace
    assert "__dev__port__host_port____txd_p__" in sys.namespace
    assert "__dev__port__host_port____txd_n__" in sys.namespace
    assert "__dev__port__host_port____rxd_p__" in sys.namespace
    assert "__dev__port__host_port____rxd_n__" in sys.namespace


def test_proto1():
    # First Proto-export test

    m = h.Module(name="TestProto1")
    ppkg = h.to_proto(m)
    assert isinstance(ppkg, h.proto.Package)
    assert len(ppkg.modules) == 1
    assert ppkg.domain == ""
    pm = ppkg.modules[0]
    assert isinstance(pm, h.proto.Module)
    assert pm.name == "hdl21.tests.test_hdl21.TestProto1"
    assert len(pm.ports) == 0
    assert len(pm.instances) == 0
    assert len(pm.default_parameters) == 0


def test_proto2():
    # Proto-export test with some hierarchy

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

    ppkg = h.to_proto(TestProto2)

    assert isinstance(ppkg, h.proto.Package)
    assert len(ppkg.modules) == 3
    assert ppkg.domain == ""

    # Check the first Module in, Child1
    pm = ppkg.modules[0]
    assert isinstance(pm, h.proto.Module)
    assert pm.name == "hdl21.tests.test_hdl21.Child1"
    assert len(pm.ports) == 2
    assert len(pm.signals) == 0
    assert len(pm.instances) == 0
    assert len(pm.default_parameters) == 0

    # Check the second Module in, Child2
    pm = ppkg.modules[1]
    assert isinstance(pm, h.proto.Module)
    assert pm.name == "hdl21.tests.test_hdl21.Child2"
    assert len(pm.ports) == 2
    assert len(pm.signals) == 0
    assert len(pm.instances) == 0
    assert len(pm.default_parameters) == 0

    # And check the parent module
    pm = ppkg.modules[2]
    assert isinstance(pm, h.proto.Module)
    assert pm.name == "hdl21.tests.test_hdl21.TestProto2"
    assert len(pm.ports) == 0
    assert len(pm.instances) == 2
    assert len(pm.default_parameters) == 0


def test_proto3():
    # Proto-export test with some slicing and concatenation

    M1 = h.Module(name="M1")
    M1.p8 = h.Inout(width=8)
    M1.p1 = h.Inout(width=1)

    M2 = h.Module(name="M2")
    M2.s = h.Signal(width=4)
    M2.i = M1()
    M2.i(p1=M2.s[0])
    M2.i(p8=h.Concat(M2.s, h.Concat(M2.s[0], M2.s[1]), M2.s[2:3]))

    ppkg = h.to_proto(M2, domain="test_proto3")

    assert isinstance(ppkg, h.proto.Package)
    assert len(ppkg.modules) == 2
    assert ppkg.domain == "test_proto3"

    # Check the child module
    pm = ppkg.modules[0]
    assert isinstance(pm, h.proto.Module)
    assert pm.name == "hdl21.tests.test_hdl21.M1"
    assert len(pm.ports) == 2
    assert len(pm.signals) == 0
    assert len(pm.instances) == 0
    assert len(pm.default_parameters) == 0

    # And check the parent module
    pm = ppkg.modules[1]
    assert isinstance(pm, h.proto.Module)
    assert pm.name == "hdl21.tests.test_hdl21.M2"
    assert len(pm.ports) == 0
    assert len(pm.signals) == 1
    assert len(pm.instances) == 1
    assert len(pm.default_parameters) == 0

    ns = h.from_proto(ppkg)

    assert isinstance(ns, SimpleNamespace)
    ns = ns.hdl21.tests.test_hdl21
    assert isinstance(ns, SimpleNamespace)
    assert isinstance(ns.M1, h.Module)
    assert len(ns.M1.ports) == 2
    assert len(ns.M1.signals) == 0
    assert len(ns.M1.instances) == 0

    assert isinstance(M2, h.Module)
    assert len(M2.ports) == 0
    assert len(M2.signals) == 1
    assert len(M2.instances) == 1
    assert "s" in M2.signals
    assert "i" in M2.instances
    inst = M2.i
    assert isinstance(inst.conns["p1"], h.signal.Slice)
    assert inst.conns["p1"].signal is M2.s
    assert inst.conns["p1"].top == 0
    assert inst.conns["p1"].bot == 0
    assert isinstance(inst.conns["p8"], h.signal.Concat)
    assert len(inst.conns["p8"].parts) == 3
    assert inst.conns["p8"].parts[0] is M2.s
    assert isinstance(inst.conns["p8"].parts[1], h.signal.Concat)
    assert isinstance(inst.conns["p8"].parts[2], h.signal.Slice)


def test_proto_roundtrip():
    # Test protobuf round-tripping

    # Create an empty (named) Module
    M1 = h.Module(name="M1")

    # Protobuf round-trip it
    ppkg = h.to_proto(M1)
    ns = h.from_proto(ppkg)

    assert isinstance(ns, SimpleNamespace)
    ns = ns.hdl21.tests.test_hdl21
    assert isinstance(ns, SimpleNamespace)
    assert isinstance(ns.M1, h.Module)
    assert len(ns.M1.signals) == 0
    assert len(ns.M1.ports) == 0
    assert len(ns.M1.instances) == 0


def test_proto_roundtrip2():

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
    M1 = ns.hdl21.tests.test_hdl21.M1
    M2 = ns.hdl21.tests.test_hdl21.M2
    assert isinstance(M1, h.Module)
    assert isinstance(M2, h.Module)

    assert len(M1.signals) == 0
    assert len(M1.ports) == 3
    assert "i" in M1.ports
    assert M1.i.direction == h.signal.PortDir.INPUT
    assert M1.i.vis == h.signal.Visibility.PORT
    assert "o" in M1.ports
    assert M1.o.direction == h.signal.PortDir.OUTPUT
    assert M1.o.vis == h.signal.Visibility.PORT
    assert "p" in M1.ports
    assert M1.p.direction == h.signal.PortDir.NONE
    assert M1.p.vis == h.signal.Visibility.PORT
    assert len(M1.instances) == 0

    assert len(M2.instances) == 3
    for i in M2.instances.values():
        assert i.of is M1
        assert i.conns["p"] is M2.p
    assert len(M2.ports) == 3
    assert len(M2.signals) == 2
    assert "s" in M2.signals
    assert "_i1_i_i0_o_" in M2.signals


def test_bigger_interfaces():
    # Test a slightly more elaborate Interface-based system

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
        jtag = Jtag(role=MsRoles.SL, port=True)
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

    # Run this through elaboration
    h.elaborate(TestSystem)

    # Post-elab checks
    assert not hasattr(TestSystem, "jtag")
    assert len(TestSystem.ports) == 0
    assert len(TestSystem.signals) == 4
    assert len(TestSystem.instances) == 2
    assert TestSystem.tester.of is Tester
    assert TestSystem.board.of is Board
    assert isinstance(TestSystem.get("_jtag_tck_"), h.Signal)
    assert isinstance(TestSystem.get("_jtag_tdi_"), h.Signal)
    assert isinstance(TestSystem.get("_jtag_tdo_"), h.Signal)
    assert isinstance(TestSystem.get("_jtag_tms_"), h.Signal)
    assert isinstance(Tester.get("_jtag_tck_"), h.Signal)
    assert len(Tester.ports) == 4
    assert len(Tester.signals) == 0
    assert len(Tester.instances) == 0
    assert Tester.get("_jtag_tck_").vis == h.signal.Visibility.PORT
    assert Tester.get("_jtag_tdo_").vis == h.signal.Visibility.PORT
    assert Tester.get("_jtag_tdi_").vis == h.signal.Visibility.PORT
    assert Tester.get("_jtag_tms_").vis == h.signal.Visibility.PORT
    assert len(Board.ports) == 4
    assert len(Board.signals) == 3  # SPI signals
    assert len(Board.instances) == 2
    assert Board.chip.of is Chip
    assert Board.flash.of is SpiFlash
    assert Board.get("_jtag_tck_").vis == h.signal.Visibility.PORT
    assert Board.get("_jtag_tdo_").vis == h.signal.Visibility.PORT
    assert Board.get("_jtag_tdi_").vis == h.signal.Visibility.PORT
    assert Board.get("_jtag_tms_").vis == h.signal.Visibility.PORT
    assert Board.get("__flash_spi_chip_spi__sck_").vis == h.signal.Visibility.INTERNAL
    assert Board.get("__flash_spi_chip_spi__cs_").vis == h.signal.Visibility.INTERNAL
    assert Board.get("__flash_spi_chip_spi__dq_").vis == h.signal.Visibility.INTERNAL
    assert len(Chip.ports) == 7
    assert len(Chip.signals) == 0
    assert len(Chip.instances) == 0
    assert Chip.get("_jtag_tck_").vis == h.signal.Visibility.PORT
    assert Chip.get("_jtag_tdo_").vis == h.signal.Visibility.PORT
    assert Chip.get("_jtag_tdi_").vis == h.signal.Visibility.PORT
    assert Chip.get("_jtag_tms_").vis == h.signal.Visibility.PORT
    assert Chip.get("_spi_sck_").vis == h.signal.Visibility.PORT
    assert Chip.get("_spi_cs_").vis == h.signal.Visibility.PORT
    assert Chip.get("_spi_dq_").vis == h.signal.Visibility.PORT
    assert len(SpiFlash.ports) == 3
    assert len(SpiFlash.signals) == 0
    assert len(SpiFlash.instances) == 0
    assert SpiFlash.get("_spi_sck_").vis == h.signal.Visibility.PORT
    assert SpiFlash.get("_spi_cs_").vis == h.signal.Visibility.PORT
    assert SpiFlash.get("_spi_dq_").vis == h.signal.Visibility.PORT


def test_signal_slice1():
    # Initial test of signal slicing

    sig = h.Signal(width=10)
    sl = sig[0]
    assert isinstance(sl, h.signal.Slice)
    assert sl.top == 0
    assert sl.bot == 0
    assert sl.width == 1
    assert sl.step == 1
    assert sl.signal is sig

    sl = sig[0:4]
    assert isinstance(sl, h.signal.Slice)
    assert sl.top == 4
    assert sl.bot == 0
    assert sl.width == 5
    assert sl.signal is sig

    sl = sig[:]
    assert isinstance(sl, h.signal.Slice)
    assert sl.top == 9
    assert sl.bot == 0
    assert sl.width == 10
    assert sl.signal is sig


def test_signal_slice2():
    # Test slicing advanced features
    sl = h.Signal(width=11)[-1]
    assert sl.top == 10
    assert sl.bot == 10
    assert sl.width == 1

    sl = h.Signal(width=11)[:-1]
    assert sl.top == 9
    assert sl.bot == 0
    assert sl.width == 10

    sl = h.Signal(width=11)[-2:]
    assert sl.top == 10
    assert sl.bot == 9
    assert sl.width == 2


def test_bad_slice1():
    # Test slicing error-cases
    with pytest.raises(TypeError):
        h.Signal(width=11)[None]

    with pytest.raises(ValueError):
        h.Signal(width=11)[11]

    h.Signal(width=11)[2:1:-1]  # OK
    with pytest.raises(ValueError):
        h.Signal(width=11)[2:1:1]  # Not OK

    h.Signal(width=11)[1:9]  # OK
    with pytest.raises(ValueError):
        h.Signal(width=11)[9:1]  # Not OK


def test_signal_concat1():
    # Initial Signal concatenation test

    c = h.Concat(h.Signal(width=1), h.Signal(width=2), h.Signal(width=3))
    assert isinstance(c, h.signal.Concat)
    assert len(c.parts) == 3
    for p in c.parts:
        assert isinstance(p, h.signal.Signal)
    assert c.width == 6

    c = h.Concat(h.Signal(width=1)[0], h.Signal(width=2)[0], h.Signal(width=3)[0])
    assert isinstance(c, h.signal.Concat)
    assert len(c.parts) == 3
    for p in c.parts:
        assert isinstance(p, h.signal.Slice)
    assert c.width == 3

    c = h.Concat(
        h.Concat(h.Signal(), h.Signal()), h.Signal(width=2), h.Signal(width=2)[:]
    )
    assert isinstance(c, h.signal.Concat)
    assert len(c.parts) == 3
    assert c.width == 6


def test_slice_module1():
    # Make use of slicing and concatenation in a module

    C = h.Module(name="C")
    C.p1 = h.Port(width=1)
    C.p4 = h.Port(width=4)
    C.p7 = h.Port(width=7)

    P = h.Module(name="P")
    C.s4 = h.Signal(width=4)
    C.s2 = h.Signal(width=2)
    P.ic = C(p1=C.s4[0], p4=C.s4, p7=h.Concat(C.s4, C.s2, C.s2[0]))

    h.elaborate(P)


def test_bad_proto_naming():
    # Test some cases which generate serialization naming conflicts
    # Same Module-names in same Python module

    with pytest.raises(RuntimeError):
        # Create a naming conflict between Module definitions
        Ma1 = h.Module(name="Ma")
        Ma2 = h.Module(name="Ma")

        @h.module
        class MaParent:
            ma1 = Ma1()
            ma2 = Ma2()

        h.to_proto(MaParent)

    with pytest.raises(RuntimeError):
        # Do the same via some functions that should be generators
        def m1():
            return h.Module(name="Ma")

        def m2():
            return h.Module(name="Ma")

        @h.module
        class MaParent:
            ma1 = m1()()
            ma2 = m2()()

        h.to_proto(MaParent)


def test_generator_recall():
    """ Test multi-calling generators """

    @h.generator
    def CallMeTwice(_: h.HasNoParams) -> h.Module:
        return h.Module()

    @h.module
    class Caller:
        m1 = CallMeTwice(h.NoParams)()
        m2 = CallMeTwice(h.NoParams)()

    # Convert to proto
    ppkg = h.to_proto(Caller)
    assert len(ppkg.modules) == 2
    assert ppkg.modules[0].name == "hdl21.tests.test_hdl21.CallMeTwice(NoParams())"
    assert ppkg.modules[1].name == "hdl21.tests.test_hdl21.Caller"

    # Convert the proto-package to a netlist, and run some (very basic) checks
    nl = StringIO()
    h.netlist(ppkg, nl)
    nl = nl.getvalue()
    assert "CallMeTwice_NoParams___" in nl
    assert "Caller" in nl

    # Round-trip back from Proto to Modules
    rt = h.from_proto(ppkg)
    ns = rt.hdl21.tests.test_hdl21
    assert isinstance(ns.Caller, h.Module)
    assert isinstance(getattr(ns, "CallMeTwice(NoParams())"), h.Module)


def test_module_as_param():
    """ Test using a `Module` as a parameter-value """

    @h.paramclass
    class HasModuleParam:
        m = h.Param(dtype=h.Module, desc="A `Module` provided as a parameter")

    @h.generator
    def UsesModuleParam(params: HasModuleParam) -> h.Module:
        return params.m  # Returns the Module unmodified

    Empty = h.Module(name="Empty")
    p = HasModuleParam(m=Empty)
    m = UsesModuleParam(p)
    m = h.elaborate(m)
    assert m == Empty


def test_mos_generator():
    """ Initial test of built-in series-Mos generator """

    Mos = h.generators.Mos
    m = Mos(Mos.Params(nser=2))

    assert isinstance(m, h.GeneratorCall)
    assert isinstance(m.arg, Mos.Params)

    m = h.elaborate(m)

    assert isinstance(m, h.Module)
    assert len(m.ports) == 4
    assert m.ports == h.primitives.Mos.ports
    assert len(m.instances) == 2
    assert "unit0" in m.instances
    assert "unit1" in m.instances
    assert isinstance(m.instances["unit0"].of, h.PrimitiveCall)
    assert isinstance(m.instances["unit1"].of, h.PrimitiveCall)
    assert m.instances["unit0"].of.params == h.primitives.MosParams()
    assert m.instances["unit1"].of.params == h.primitives.MosParams()
    assert len(m.signals) == 1
    assert "_unit1_s_unit0_d_" in m.signals

    ppkg = h.to_proto(m)
    assert isinstance(ppkg, h.proto.Package)


def test_series_parallel_generator():
    """ Initial test of the general-purpose series-parallel generator """

    from hdl21.generators import SeriesPar

    @h.module
    class M:  # Unit cell
        a, b, c, d, e, f, g = h.Ports(7)

    params = SeriesPar.Params(unit=M, npar=2, nser=2, series_conns=["a", "b"])
    m = SeriesPar(params)

    assert isinstance(m, h.GeneratorCall)
    assert isinstance(m.arg, SeriesPar.Params)

    m = h.elaborate(m)

    assert isinstance(m, h.Module)
    assert len(m.ports) == 7
    assert m.ports == M.ports
    assert len(m.instances) == 4
    assert "unit_0_0" in m.instances
    assert "unit_0_1" in m.instances
    assert "unit_1_0" in m.instances
    assert "unit_1_1" in m.instances

    for inst in m.instances.values():
        assert inst.of is M
    assert len(m.signals) == 2
    assert "_unit_0_1_a_unit_0_0_b_" in m.signals
    assert "_unit_1_1_a_unit_1_0_b_" in m.signals

    ppkg = h.to_proto(m)
    assert isinstance(ppkg, h.proto.Package)


def test_instance_mult():
    """ Initial tests of instance-array-generation by multiplication """

    Child = h.Module(name="Child")
    Parent = h.Module(name="Parent")

    # Create an array via multiplication
    Parent.child = Child() * 5  # Lotta kids here

    # Check that the array is created correctly
    assert isinstance(Parent.child, h.InstArray)
    assert Parent.child.n == 5
    assert Parent.child.of is Child

    # Test elaboration
    h.elaborate(Parent)

    # Post-elaboration checks
    assert len(Parent.instances) == 5
    assert len(Parent.instarrays) == 0
    for inst in Parent.instances.values():
        assert inst.of is Child

    # Create another, this time via right-mul
    Parent = h.Module(name="Parent")
    Parent.child = 11 * Child()  # Getting even more kids

    # Check that the array is created correctly
    assert isinstance(Parent.child, h.InstArray)
    assert Parent.child.n == 11
    assert Parent.child.of is Child

    # Test elaboration
    h.elaborate(Parent)

    # Post-elaboration checks
    assert len(Parent.instances) == 11
    assert len(Parent.instarrays) == 0
    for inst in Parent.instances.values():
        assert inst.of is Child


def test_instance_mult2():
    """ Test connecting to multiplication-generated InstArrays """

    @h.module
    class Child:
        p = h.Port()

    @h.module
    class Parent:
        a = h.Signal(width=3)
        child = (Child() * 3)(p=a)

    assert len(Parent.instances) == 0
    assert len(Parent.instarrays) == 1

    h.elaborate(Parent)

    # Check that array-flattening completed correctly
    assert len(Parent.instances) == 3
    assert len(Parent.instarrays) == 0
    assert Parent.get("_child_0_").of is Child
    assert Parent.get("_child_1_").of is Child
    assert Parent.get("_child_2_").of is Child
    assert Parent.get("_child_0_").conns["p"] == Parent.a[0]
    assert Parent.get("_child_1_").conns["p"] == Parent.a[1]
    assert Parent.get("_child_2_").conns["p"] == Parent.a[2]


def test_instance_mult3():
    """ Test connecting to an "already connected" Instance """

    @h.module
    class Child:
        p = h.Port()

    @h.module
    class Parent:
        a = h.Signal(width=3)
        child = 3 * Child(p=a)  # <= this the one diff here from test_instance_mult2

    h.elaborate(Parent)

    # Check that array-flattening completed correctly
    assert len(Parent.instances) == 3
    assert len(Parent.instarrays) == 0
    assert Parent.get("_child_0_").of is Child
    assert Parent.get("_child_1_").of is Child
    assert Parent.get("_child_2_").of is Child
    assert Parent.get("_child_0_").conns["p"] == Parent.a[0]
    assert Parent.get("_child_1_").conns["p"] == Parent.a[1]
    assert Parent.get("_child_2_").conns["p"] == Parent.a[2]


def test_instance_mult4():
    """ Test connecting non-unit-width Arrays """

    @h.module
    class Child:
        a = h.Port(width=11)
        b = h.Port(width=16)

    @h.module
    class Parent:
        a = h.Signal(width=11)
        b = h.Signal(width=48)
        child = 3 * Child(a=a, b=b)

    h.elaborate(Parent)

    # Check that array-flattening completed correctly
    assert len(Parent.instances) == 3
    assert len(Parent.instarrays) == 0
    assert Parent.get("_child_0_").of is Child
    assert Parent.get("_child_1_").of is Child
    assert Parent.get("_child_2_").of is Child
    assert Parent.get("_child_0_").conns["a"] == Parent.a
    assert Parent.get("_child_1_").conns["a"] == Parent.a
    assert Parent.get("_child_2_").conns["a"] == Parent.a
    assert Parent.get("_child_0_").conns["b"] == Parent.b[0:15]
    assert Parent.get("_child_1_").conns["b"] == Parent.b[16:31]
    assert Parent.get("_child_2_").conns["b"] == Parent.b[32:47]


def test_netlist_fmts():
    """ Test netlisting basic types to several formats """

    @h.module
    class Bot:
        s = h.Input(width=3)
        p = h.Output()

    @h.module
    class Top:
        s = h.Signal(width=3)
        p = h.Output()
        b = Bot(s=s, p=p)

    # Convert to proto
    ppkg = h.to_proto(Top)
    assert len(ppkg.modules) == 2
    assert ppkg.modules[0].name == "hdl21.tests.test_hdl21.Bot"
    assert ppkg.modules[1].name == "hdl21.tests.test_hdl21.Top"

    # Convert the proto-package to a netlist
    nl = StringIO()
    h.netlist(ppkg, nl, "spectre")
    nl = nl.getvalue()

    # Basic checks on its contents
    assert "subckt Bot" in nl
    assert "+  s_2 s_1 s_0 p" in nl
    assert "subckt Top" in nl
    assert "b\n" in nl
    assert "+  ( s_2 s_1 s_0 p  )" in nl
    assert "+  p" in nl
    assert "+  Bot " in nl

    # Convert the proto-package to another netlist format
    nl = StringIO()
    h.netlist(ppkg, nl, "verilog")
    nl = nl.getvalue()

    # Basic checks on its contents
    assert "module Bot" in nl
    assert "input wire [2:0] s," in nl
    assert "output wire p" in nl
    assert "endmodule // Bot" in nl
    assert "module Top" in nl
    assert ".s(s)" in nl
    assert ".p(p)" in nl
    assert "endmodule // Top" in nl


def test_bad_width_conn():
    """ Test invalid connection-widths """
    c = h.Module(name="c")
    c.p = h.Port(width=3)  # Width-3 Port
    q = h.Module(name="q")
    q.s = h.Signal(width=5)  # Width-5 Signal
    q.c = c(p=q.s)  # <= Bad connection here

    with pytest.raises(RuntimeError):
        h.elaborate(q)


def test_bad_intf_conn():
    """ Test invalid Interface connections """

    @h.interface
    class P:
        p = h.Signal(width=3)

    @h.interface
    class R:
        z = h.Signal(width=11)

    c = h.Module(name="c")
    c.p = P(port=True)  # `P`-type Interface
    q = h.Module(name="q")
    q.r = R()  # `R`-type Interface
    q.c = c(p=q.r)  # <= Bad connection here

    with pytest.raises(RuntimeError):
        h.elaborate(q)
