""" 
# Hdl21 Unit Tests 
"""

import copy, pytest
from enum import Enum, EnumMeta, auto

from pydantic import ValidationError

# Import the PUT (package under test)
import hdl21 as h


def test_version():
    assert h.__version__ == "2.0.dev0"


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

    assert m.name == "gen1(w=3)"
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
    assert m.name == "g2(f=1e-11)"


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
    assert HasGen.a.of.result.name == "g3a(width=1)"
    assert isinstance(HasGen.b, h.Instance)
    assert isinstance(HasGen.b.of, h.GeneratorCall)
    assert isinstance(HasGen.b.of.result, h.Module)
    assert HasGen.b.of.result.name == "g3b(width=5)"
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
    assert uname1 == "3dcc309796996b3a8a61db66631c5a93"


def test_bad_params1():
    # Test a handful of errors Params and paramclasses should raise.

    from hdl21 import (
        paramclass,
        Param,
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
    assert len(b2.bundles) == 0
    assert len(b2.ports) == 0
    assert len(b2.signals) == 2
    assert "t2_inp_t1_out" in b2.signals
    assert "t2_out_t1_inp" in b2.signals


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


def test_bundle1():
    # Create an bundle

    i1 = h.Bundle(name="MyFirstBundle")
    i1.s1 = h.Signal()
    i1.s2 = h.Signal()

    assert isinstance(i1, h.Bundle)
    assert isinstance(i1.s1, h.Signal)
    assert isinstance(i1.s2, h.Signal)

    ii1 = i1()
    assert isinstance(ii1, h.BundleInstance)
    assert ii1.role is None
    assert ii1.port == False


def test_bundle2():
    # Wire up a few Modules via bundles

    MySecondBundle = h.Bundle(name="MySecondBundle")
    MySecondBundle.s = h.Signal()

    m1 = h.Module(name="M1")
    m1.i = MySecondBundle(port=True)
    m2 = h.Module(name="M2")
    m2.i = MySecondBundle(port=True)

    # Now create a parent Module connecting the two
    m3 = h.Module(name="M3")
    m3.i1 = m1()
    m3.i2 = m2(i=m3.i1.i)
    assert "i2_i_i1_i" not in m3.namespace

    # First run the "implicit bundles" pass, and see that an explicit one is created
    from hdl21.elab import ElabPass

    m3 = h.elaborate(m3, passes=[ElabPass.RESOLVE_PORT_REFS])
    assert isinstance(m3, h.Module)
    assert isinstance(m3.i1, h.Instance)
    assert isinstance(m3.i2, h.Instance)
    assert "i2_i_i1_i" in m3.namespace

    # Now elaborate it the rest of the way, to scalar signals
    m3 = h.elaborate(m3)
    assert "i2_i_i1_i" not in m3.namespace
    assert "i2_i_i1_i_s" in m3.namespace
    assert isinstance(m3.get("i2_i_i1_i_s"), h.Signal)
    assert m3.get("i2_i_i1_i_s") in m3.i1.conns.values()


def test_bundle3():
    # Test the bundle-definition decorator

    @h.bundle
    class Diff:  # Differential Signal Bundle
        p = h.Signal()
        n = h.Signal()

    @h.bundle
    class DisplayPort:  # DisplayPort, kinda
        main_link = Diff()
        aux = h.Signal()

    assert isinstance(DisplayPort, h.Bundle)
    assert isinstance(DisplayPort(), h.BundleInstance)
    assert isinstance(DisplayPort.main_link, h.BundleInstance)
    assert isinstance(DisplayPort.main_link.p, h.BundleRef)
    assert isinstance(DisplayPort.main_link.n, h.BundleRef)
    assert isinstance(DisplayPort.aux, h.Signal)
    assert isinstance(Diff, h.Bundle)
    assert isinstance(Diff(), h.BundleInstance)
    assert isinstance(Diff.p, h.Signal)
    assert isinstance(Diff.n, h.Signal)

    # Instantiate one in a Module
    m = h.Module(name="M")
    m.dp = DisplayPort()
    assert isinstance(m.dp, h.BundleInstance)
    assert len(m.bundles) == 1
    assert len(m.signals) == 0

    # And elaborate it
    h.elaborate(m)

    assert not hasattr(m, "dp")
    assert len(m.bundles) == 0
    assert len(m.signals) == 3
    assert isinstance(m.get("dp_aux"), h.Signal)
    assert isinstance(m.get("dp_main_link_p"), h.Signal)
    assert isinstance(m.get("dp_main_link_n"), h.Signal)


def test_bundle4():
    # Test bundle roles

    @h.bundle
    class Diff:  # Differential Signal Bundle
        p = h.Signal()
        n = h.Signal()

    @h.bundle
    class HasRoles:  # An Bundle with Roles
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
    assert isinstance(HasRoles, h.Bundle)
    assert isinstance(HasRoles.roles, EnumMeta)
    assert isinstance(HasRoles.Roles, EnumMeta)
    assert isinstance(hr, h.BundleInstance)
    assert isinstance(HasRoles.tx, h.Signal)
    assert isinstance(HasRoles.rx, h.Signal)
    assert isinstance(HasRoles.txd, h.BundleInstance)
    assert isinstance(HasRoles.rxd, h.BundleInstance)

    @h.module
    class Host:
        # A thing with a HOST-roled bundle-port
        hr = HasRoles(port=True, role=HasRoles.Roles.HOST)

    @h.module
    class Device:
        # A thing with a DEVICE-roled bundle-port
        hr = HasRoles(port=True, role=HasRoles.Roles.DEVICE)

    @h.module
    class System:
        # Parent system-module including a host and device
        host = Host()
        devc = Device(hr=host.hr)

    assert isinstance(System, h.Module)
    assert isinstance(System.host, h.Instance)
    assert isinstance(System.devc, h.Instance)
    assert "devc_hr_host_hr" not in System.namespace

    # First run the "implicit bundles" pass, and see that an explicit one is created
    from hdl21.elab import ElabPass

    sys = h.elaborate(System, passes=[ElabPass.RESOLVE_PORT_REFS])
    assert "devc_hr_host_hr" in sys.namespace

    # Now expand the rest of the way, down to scalar signals
    # Check that bundle went away, and its constituent signals replaced it
    sys = h.elaborate(sys)
    assert "devc_hr_host_hr" not in sys.namespace
    assert "devc_hr_host_hr_tx" in sys.namespace
    assert "devc_hr_host_hr_rx" in sys.namespace
    assert "devc_hr_host_hr_txd_p" in sys.namespace
    assert "devc_hr_host_hr_txd_n" in sys.namespace
    assert "devc_hr_host_hr_rxd_p" in sys.namespace
    assert "devc_hr_host_hr_rxd_n" in sys.namespace


def test_bigger_bundles():
    """ Test a slightly more elaborate Bundle-based system """

    class HostDevice(Enum):
        HOST = auto()
        DEVICE = auto()

    @h.bundle
    class Jtag:
        # Jtag Bundle

        roles = HostDevice
        tck, tdi, tms = h.Signals(3, src=roles.HOST, dest=roles.DEVICE)
        tdo = h.Signal(src=roles.DEVICE, dest=roles.HOST)

    @h.bundle
    class Uart:
        # Uart Bundle
        class Roles(Enum):
            # Uart roles are essentially peers, here named `ME` and `YOU`.
            # Essentially everything will use the role `ME`,
            # except for interconnect which swaps between the two.
            ME = auto()
            YOU = auto()

        tx = h.Signal(src=Roles.ME, dest=Roles.YOU)
        rx = h.Signal(src=Roles.YOU, dest=Roles.ME)

    @h.bundle
    class Spi:
        # Spi Bundle
        roles = HostDevice
        sck, cs = h.Signals(2, src=roles.HOST, dest=roles.DEVICE)
        dq = h.Signal(src=roles.DEVICE, dest=roles.HOST, width=4)

    @h.module
    class Chip:
        spi = Spi(role=HostDevice.HOST, port=True)
        jtag = Jtag(role=HostDevice.DEVICE, port=True)
        uart = Uart(role=Uart.Roles.ME, port=True)
        ...  # Actual internal content, which likely connects these down *many* levels of hierarchy

    @h.module
    class SpiFlash:
        # A typical flash memory with a SPI port
        spi = Spi(role=HostDevice.DEVICE, port=True)

    @h.module
    class Board:
        # A typical embedded board, featuring a custom chip, SPI-connected flash, and JTAG port
        jtag = Jtag(role=HostDevice.DEVICE, port=True)
        uart = Uart(role=Uart.Roles.ME, port=True)

        chip = Chip(jtag=jtag, uart=uart)
        flash = SpiFlash(spi=chip.spi)

    @h.module
    class Tester:
        # A typical test-widget with a JTAG port
        jtag = Jtag(role=HostDevice.HOST, port=True)
        uart = Uart(role=Uart.Roles.ME, port=True)

    @h.module
    class TestSystem:
        # A system in which `Tester` can test `Board`
        jtag = Jtag()

        tester = Tester(jtag=jtag)
        board = Board(jtag=jtag)

        # Connect UART, swapping `rx` and `tx`
        u0, u1 = h.Signals(2)
        board.uart = h.AnonymousBundle(tx=u0, rx=u1)
        tester.uart = h.AnonymousBundle(rx=u0, tx=u1)

    assert isinstance(TestSystem.jtag, h.BundleInstance)
    assert isinstance(TestSystem.tester, h.Instance)
    assert isinstance(TestSystem.board, h.Instance)

    assert isinstance(TestSystem.tester.uart, h.PortRef)
    assert isinstance(TestSystem.board.uart, h.PortRef)

    # Run this through elaboration
    h.elaborate(TestSystem)

    # Post-elab checks
    # TestSystem
    assert isinstance(TestSystem.tester, h.Instance)
    assert isinstance(TestSystem.board, h.Instance)
    assert TestSystem.tester.of is Tester
    assert TestSystem.board.of is Board
    assert not hasattr(TestSystem, "jtag")
    assert not hasattr(TestSystem, "uart")
    assert "u0" in TestSystem.namespace
    assert "u1" in TestSystem.namespace
    assert len(TestSystem.ports) == 0
    assert len(TestSystem.signals) == 6
    assert len(TestSystem.instances) == 2
    assert isinstance(TestSystem.get("u0"), h.Signal)
    assert isinstance(TestSystem.get("u1"), h.Signal)
    assert isinstance(TestSystem.get("jtag_tck"), h.Signal)
    assert isinstance(TestSystem.get("jtag_tdi"), h.Signal)
    assert isinstance(TestSystem.get("jtag_tdo"), h.Signal)
    assert isinstance(TestSystem.get("jtag_tms"), h.Signal)

    # Tester
    assert len(Tester.ports) == 6
    assert len(Tester.signals) == 0
    assert len(Tester.instances) == 0
    assert isinstance(Tester.get("jtag_tck"), h.Signal)
    assert Tester.get("jtag_tck").vis == h.signal.Visibility.PORT
    assert Tester.get("jtag_tdo").vis == h.signal.Visibility.PORT
    assert Tester.get("jtag_tdi").vis == h.signal.Visibility.PORT
    assert Tester.get("jtag_tms").vis == h.signal.Visibility.PORT
    assert Tester.get("uart_tx").vis == h.signal.Visibility.PORT
    assert Tester.get("uart_rx").vis == h.signal.Visibility.PORT

    # Board
    assert len(Board.ports) == 6
    assert len(Board.signals) == 3  # SPI signals
    assert len(Board.instances) == 2
    assert Board.chip.of is Chip
    assert Board.flash.of is SpiFlash
    assert Board.get("jtag_tck").vis == h.signal.Visibility.PORT
    assert Board.get("jtag_tdo").vis == h.signal.Visibility.PORT
    assert Board.get("jtag_tdi").vis == h.signal.Visibility.PORT
    assert Board.get("jtag_tms").vis == h.signal.Visibility.PORT
    assert Board.get("uart_tx").vis == h.signal.Visibility.PORT
    assert Board.get("uart_rx").vis == h.signal.Visibility.PORT
    assert Board.get("flash_spi_chip_spi_sck").vis == h.signal.Visibility.INTERNAL
    assert Board.get("flash_spi_chip_spi_cs").vis == h.signal.Visibility.INTERNAL
    assert Board.get("flash_spi_chip_spi_dq").vis == h.signal.Visibility.INTERNAL

    # Chip
    assert len(Chip.ports) == 9
    assert len(Chip.signals) == 0
    assert len(Chip.instances) == 0
    assert Chip.get("jtag_tck").vis == h.signal.Visibility.PORT
    assert Chip.get("jtag_tdo").vis == h.signal.Visibility.PORT
    assert Chip.get("jtag_tdi").vis == h.signal.Visibility.PORT
    assert Chip.get("jtag_tms").vis == h.signal.Visibility.PORT
    assert Chip.get("spi_sck").vis == h.signal.Visibility.PORT
    assert Chip.get("spi_cs").vis == h.signal.Visibility.PORT
    assert Chip.get("spi_dq").vis == h.signal.Visibility.PORT
    assert Chip.get("uart_tx").vis == h.signal.Visibility.PORT
    assert Chip.get("uart_rx").vis == h.signal.Visibility.PORT

    # SpiFlash
    assert len(SpiFlash.ports) == 3
    assert len(SpiFlash.signals) == 0
    assert len(SpiFlash.instances) == 0
    assert SpiFlash.get("spi_sck").vis == h.signal.Visibility.PORT
    assert SpiFlash.get("spi_cs").vis == h.signal.Visibility.PORT
    assert SpiFlash.get("spi_dq").vis == h.signal.Visibility.PORT


def test_signal_slice1():
    # Initial test of signal slicing

    sig = h.Signal(width=10)
    sl = sig[0]
    assert isinstance(sl, h.signal.Slice)
    assert sl.top == 1
    assert sl.bot == 0
    assert sl.width == 1
    assert sl.step is None
    assert sl.signal is sig

    sl = sig[0:5]
    assert isinstance(sl, h.signal.Slice)
    assert sl.top == 5
    assert sl.bot == 0
    assert sl.width == 5
    assert sl.step is None
    assert sl.signal is sig

    sl = sig[:]
    assert isinstance(sl, h.signal.Slice)
    assert sl.top == 10
    assert sl.bot == 0
    assert sl.width == 10
    assert sl.step is None
    assert sl.signal is sig


def test_signal_slice2():
    # Test slicing advanced features
    sl = h.Signal(width=11)[-1]
    assert sl.top == 11
    assert sl.bot == 10
    assert sl.step is None
    assert sl.width == 1

    sl = h.Signal(width=11)[:-1]
    assert sl.top == 10
    assert sl.bot == 0
    assert sl.step is None
    assert sl.width == 10

    sl = h.Signal(width=11)[-2:]
    assert sl.top == 11
    assert sl.bot == 9
    assert sl.step is None
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
    """ Make use of slicing and concatenation in a module """

    C = h.Module(name="C")
    C.p1 = h.Port(width=1)
    C.p4 = h.Port(width=4)
    C.p7 = h.Port(width=7)

    P = h.Module(name="P")
    P.s4 = h.Signal(width=4)
    P.s2 = h.Signal(width=2)
    P.ic = C(p1=P.s4[0], p4=P.s4, p7=h.Concat(P.s4, P.s2, P.s2[0]))

    h.elaborate(P)


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
    assert "unit1_s_unit0_d" in m.signals


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
    assert "unit_0_1_a_unit_0_0_b" in m.signals
    assert "unit_1_1_a_unit_1_0_b" in m.signals


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
    assert Parent.get("child_0").of is Child
    assert Parent.get("child_1").of is Child
    assert Parent.get("child_2").of is Child
    assert Parent.get("child_0").conns["p"] == Parent.a[0]
    assert Parent.get("child_1").conns["p"] == Parent.a[1]
    assert Parent.get("child_2").conns["p"] == Parent.a[2]


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
    assert Parent.get("child_0").of is Child
    assert Parent.get("child_1").of is Child
    assert Parent.get("child_2").of is Child
    assert Parent.get("child_0").conns["p"] == Parent.a[0]
    assert Parent.get("child_1").conns["p"] == Parent.a[1]
    assert Parent.get("child_2").conns["p"] == Parent.a[2]


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
    assert Parent.get("child_0").of is Child
    assert Parent.get("child_1").of is Child
    assert Parent.get("child_2").of is Child
    assert Parent.get("child_0").conns["a"] == Parent.a
    assert Parent.get("child_1").conns["a"] == Parent.a
    assert Parent.get("child_2").conns["a"] == Parent.a
    assert Parent.get("child_0").conns["b"] == Parent.b[0:16]
    assert Parent.get("child_1").conns["b"] == Parent.b[16:32]
    assert Parent.get("child_2").conns["b"] == Parent.b[32:48]


def test_bad_width_conn():
    """ Test invalid connection-widths """
    c = h.Module(name="c")
    c.p = h.Port(width=3)  # Width-3 Port
    q = h.Module(name="q")
    q.s = h.Signal(width=5)  # Width-5 Signal
    q.c = c(p=q.s)  # <= Bad connection here

    with pytest.raises(RuntimeError):
        h.elaborate(q)


def test_bad_bundle_conn():
    """ Test invalid Bundle connections """

    @h.bundle
    class P:
        p = h.Signal(width=3)

    @h.bundle
    class R:
        z = h.Signal(width=11)

    @h.module
    class C:
        p = P(port=True)  # `P`-type Bundle

    @h.module
    class Q:
        r = R()  # `R`-type Bundle
        c = C(p=r)  # <= Bad connection here

    with pytest.raises(RuntimeError):
        h.elaborate(Q)


def test_illegal_module_attrs():
    """ Test attempting to add illegal attributes """

    m = h.Module()
    with pytest.raises(TypeError):
        m.a = list()

    with pytest.raises(TypeError):

        @h.module
        class M:
            a = list()

    @h.module
    class C:
        ...

    with pytest.raises(TypeError):
        C.b = TabError

    # Use combinations of legal attributes

    m = h.Module(name="m")
    with pytest.raises(TypeError):
        m.p = 5
    with pytest.raises(TypeError):
        m.z = dict(a=h.Signal())
    with pytest.raises(TypeError):
        m.q = [h.Port()]
    with pytest.raises(TypeError):
        m.p = (h.Input(), h.Output())
    with pytest.raises(TypeError):
        m.func = lambda _: None
    with pytest.raises(TypeError):

        @h.module
        class HasMethod:
            def fail(self):
                ...


def test_copy_signal():
    """ Copying a Signal """
    copy.copy(h.Signal())


def test_copy_bundle_instance():
    """ Copying a BundleInstance """
    # This generally fails when run in the debugger, but seems alright stand-alone (?)
    copy.copy(h.BundleInstance(name="inst", of=h.Bundle()))


def test_bundle_destructure():
    """ Test de-structuring bundles to individual Signals """

    @h.bundle
    class B:
        w1 = h.Signal(width=1)
        w3 = h.Signal(width=3)

    @h.module
    class Child:
        w1 = h.Port(width=1)
        w3 = h.Port(width=3)

    @h.module
    class Parent:
        b = B()  # `B`-type Bundle instance
        c = Child(w1=b.w1, w3=b.w3)  # `Child`-type instance, connected to `b`

    h.elaborate(Parent)

    assert len(Parent.instances) == 1
    assert len(Parent.signals) == 2
    assert "b_w1" in Parent.signals
    assert "b_w3" in Parent.signals
    assert Parent.c.conns["w1"] is Parent.signals["b_w1"]
    assert Parent.c.conns["w3"] is Parent.signals["b_w3"]


def test_orphanage():
    """ Test that orphaned Module-attributes fail at elaboration """

    m1 = h.Module(name="m1")
    m1.s = h.Signal()  # Signal `s` is now "parented" by `m1`

    m2 = h.Module(name="m2")
    m2.y = m1.s  # Now `s` has been "orphaned" (or perhaps "cradle-robbed") by `m2`

    # Note elaborating `m2` continues to work
    h.elaborate(m2)

    with pytest.raises(RuntimeError):
        # Elaborating `m1` should fail, since `s` is orphaned
        h.elaborate(m1)


def test_orphanage2():
    """ Test orphaning a bundle instance """

    @h.bundle
    class B:
        bb = h.Signal(width=1)

    b = B()  # Instance of `B`-type Bundle, to be orphaned

    m1 = h.Module(name="m1")
    m1.b = b
    m2 = h.Module(name="m2")
    m2.b = b

    # Note elaborating `m2` continues to work
    h.elaborate(m2)

    with pytest.raises(RuntimeError):
        # Elaborating `m1` should fail, since `s` is orphaned
        h.elaborate(m1)


def test_orphanage3():
    """ Test orphaning an instance """
    I = h.Module(name="I")
    i = I()  # Instance to be orphaned

    m1 = h.Module(name="m1")
    m1.i = i
    m2 = h.Module(name="m2")
    m2.i = i

    # Note elaborating `m2` continues to work
    h.elaborate(m2)

    with pytest.raises(RuntimeError):
        # Elaborating `m1` should fail, since `s` is orphaned
        h.elaborate(m1)


def test_orphanage4():
    """ Test an orphan Instance connection """

    m1 = h.Module(name="m1")
    m1.p = h.Port() 

    # The "orphan signal" will not be owned by any module
    the_orphan_signal = h.Signal()
    m2 = h.Module(name="m2")
    m2.i = m1(p=the_orphan_signal) # <= Problem's here

    # Note elaborating `m1` continues to work
    h.elaborate(m1)

    with pytest.raises(RuntimeError):
        # Elaborating `m2` should fail
        h.elaborate(m2)


@pytest.mark.xfail(reason="#6 https://github.com/dan-fritchman/Hdl21/issues/6")
def test_wrong_decorator():
    """ Mistake `Module` for `module` """

    with pytest.raises(RuntimeError):

        @h.Module  # Bad!
        class M:
            ...


def test_elab_noconn():
    """ Initial test of elaborating a `NoConn` """

    @h.module
    class Inner:
        p = h.Port()

    @h.module
    class HasNoConn:
        i1 = Inner()
        i1.p = h.NoConn()

    h.elaborate(HasNoConn)

    assert len(HasNoConn.signals) == 1


def test_bad_noconn():
    """ Test that a doubly-connected `NoConn` should fail """

    @h.module
    class Inner:
        p = h.Port()

    @h.module
    class Bad:
        # Create two instances of `Inner`
        i1 = Inner()
        i2 = Inner()

        # Connect the first to a `NoConn`
        i1.p = h.NoConn()
        # And then connect the second to the first.
        # Herein lies the "problem"
        i2.p = i1.p

    with pytest.raises(RuntimeError):
        h.elaborate(Bad)


def test_array_concat_conn():
    """ Test connecting a `Concat` to an `InstArray` """

    Child = h.Module(name="Child")
    Child.p3 = h.Input(width=3)
    Child.p5 = h.Input(width=5)

    Parent = h.Module(name="Parent")
    Parent.s5 = h.Signal(width=5)
    Parent.s9 = h.Signal(width=9)
    Parent.c = 2 * Child()
    Parent.c.p3 = Parent.s5[0:3]
    Parent.c.p5 = h.Concat(Parent.s5[3], Parent.s9)


def test_slice_resolution():
    """ Test resolutions of slice combinations """

    # This is a very private import of the slice-resolver function
    from hdl21.elab.elaborators.slices import _resolve_slice

    # Slice of a Signal
    s = h.Signal(width=5)
    assert _resolve_slice(s[0]) == s[0]

    # Slice of a Concat
    s1 = h.Signal(name="s1", width=5)
    s2 = h.Signal(name="s2", width=5)
    c = h.Concat(s1, s2)
    assert _resolve_slice(c[0]) == s1[0]
    assert _resolve_slice(c[1]) == s1[1]
    assert _resolve_slice(c[2]) == s1[2]
    assert _resolve_slice(c[3]) == s1[3]
    assert _resolve_slice(c[4]) == s1[4]
    assert _resolve_slice(c[5]) == s2[0]
    assert _resolve_slice(c[6]) == s2[1]
    assert _resolve_slice(c[7]) == s2[2]
    assert _resolve_slice(c[8]) == s2[3]
    assert _resolve_slice(c[9]) == s2[4]

    # Slice of a Slice
    sa = h.Signal(name="sa", width=5)
    assert _resolve_slice(sa[2:5][0]) == sa[2]
    assert _resolve_slice(sa[2:5][1]) == sa[3]
    assert _resolve_slice(sa[2:5][2]) == sa[4]

    assert _resolve_slice(sa[:][0]) == sa[0]
    assert _resolve_slice(sa[:][1]) == sa[1]
    assert _resolve_slice(sa[:][2]) == sa[2]
    assert _resolve_slice(sa[:][3]) == sa[3]
    assert _resolve_slice(sa[:][4]) == sa[4]

    # Check a concatenation case. Note `Concat` does not support equality, so compare parts.
    assert _resolve_slice(sa[:][0:4]).parts == (sa[0], sa[1], sa[2], sa[3])


def test_common_attr_errors():
    """ Test that common errors provide helpful feedback. 
    For example, adding `Module`s where one wants an `Instance`. """

    M = h.Module(name="M")

    # Module assignment, where we'd want an Instance `M.i = I()`
    I = h.Module(name="I")
    with pytest.raises(TypeError) as einfo:
        M.i = I  # Bad - Module
    assert "Did you mean" in str(einfo.value)
    assert "`Module`" in str(einfo.value)
    M.i = I()  # Good - Instance

    # Primitive assignment
    from hdl21.primitives import R

    with pytest.raises(TypeError) as einfo:
        M.r = R  # Fail - Primitive
    assert "Did you mean" in str(einfo.value)
    assert "`Primitive`" in str(einfo.value)
    with pytest.raises(TypeError) as einfo:
        M.r = R(R.Params(r=1))  # Fail - Primitive Call
    assert "Did you mean" in str(einfo.value)
    assert "`PrimitiveCall`" in str(einfo.value)
    M.r = R(R.Params(r=1))()  # Good - Instances (granted incompletely connected)

    # Generator assignment
    @h.generator
    def G(p: h.HasNoParams) -> h.Module:
        return h.Module()

    with pytest.raises(TypeError) as einfo:
        M.g = G  # Bad - Generator
    assert "Did you mean" in str(einfo.value)
    assert "`Generator`" in str(einfo.value)
    with pytest.raises(TypeError) as einfo:
        M.g = G(h.NoParams)  # Bad - GeneratorCall
    assert "Did you mean" in str(einfo.value)
    assert "`GeneratorCall`" in str(einfo.value)
    M.g = G(h.NoParams)()  # Good - Instance

    X = h.ExternalModule(name="X", port_list=[])
    with pytest.raises(TypeError) as einfo:
        M.x = X  # Bad - ExternalModule
    assert "Did you mean" in str(einfo.value)
    assert "`ExternalModule`" in str(einfo.value)
    with pytest.raises(TypeError) as einfo:
        M.x = X()  # Bad - ExternalModuleCall
    assert "Did you mean" in str(einfo.value)
    assert "`ExternalModuleCall`" in str(einfo.value)
    M.x = X()()  # Good - Instance


def test_generator_call_by_kwargs():
    """ Test the capacity for generators to create their param-classes inline. """

    @h.paramclass
    class P:
        a = h.Param(dtype=int, desc="a")
        b = h.Param(dtype=float, desc="b")
        c = h.Param(dtype=str, desc="c")

    @h.generator
    def M(p: P) -> h.Module:
        return h.Module()

    # Call without constructing a `P`
    m = M(a=1, b=2.0, c="3")

    assert isinstance(m, h.GeneratorCall)
    m = h.elaborate(m)
    assert isinstance(m, h.Module)

    # Check that type-checking continue
    m = M(a=TabError, b=TabError, c=TabError)
    assert isinstance(m, h.GeneratorCall)
    with pytest.raises(ValidationError):
        m = h.elaborate(m)


def test_instance_array_portrefs():
    """ Test Instance Arrays connected by port-references """

    Inv = h.ExternalModule(
        name="Inv", port_list=[h.Input(name="i"), h.Output(name="z"),],
    )

    m = h.Module(name="TestArrayPortRef")
    m.a, m.b = h.Signals(2, width=4)

    # Create an InstArray
    m.inva = 4 * Inv()(i=m.a)
    # And another which connects to it via PortRef
    m.invb = 4 * Inv()(i=m.inva.z, z=m.b)

    h.elaborate(m)

    assert len(m.instances) == 8
    assert len(m.instarrays) == 0


def test_array_bundle():
    """ Test bundle-valued connections to instance arrays. """

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class HasB:
        b = B(port=True)

    @h.module
    class HasArr:
        b = B()
        bs = 11 * HasB(b=b)

    # Elaborate this,
    h.elaborate(HasArr)

    assert len(HasArr.signals) == 1
    assert len(HasArr.instances) == 11
    assert len(HasArr.instarrays) == 0
    for inst in HasArr.instances.values():
        assert inst.conns.get("b_s", None) is HasArr.b_s


@pytest.mark.xfail(reason="#19 https://github.com/dan-fritchman/Hdl21/issues/19")
def test_sub_bundle_conn():
    """ Test connecting via BundleRef to a sub-Bundle """

    @h.bundle
    class B1:
        s = h.Signal()

    @h.bundle
    class B2:
        b1 = B1()

    @h.module
    class HasB1:
        b1 = B1(port=True)

    @h.module
    class HasB2:
        b2 = B2()
        h = HasB1(b1=b2.b1)

    h.elaborate(HasB2)


def test_anon_bundle_port_conn():
    """ Test connecting via PortRef to an AnonymousBundle """

    @h.bundle
    class B:
        s = h.Signal()

    @h.module
    class HasB:
        b = B(port=True)

    @h.module
    class Top:
        s = h.Signal()
        h1 = HasB(b=h.AnonymousBundle(s=s))
        h2 = HasB(b=h1.b)
        h3 = HasB(b=h2.b)

    # Elaborate to flesh this out
    h.elaborate(Top)

    # Check this resolved to a single Signal in Top
    assert len(Top.signals) == 1
    assert len(Top.bundles) == 0
    assert len(Top.instances) == 3

    # And check that Signal is connected to all three Instances
    assert Top.h1.b_s is Top.s
    assert Top.h2.b_s is Top.s
    assert Top.h3.b_s is Top.s


def test_multiple_signals_in_port_group():
    """ Test, or at least try to test, jamming more than one Signal 
    into the `group` concept used by the `ResolvePortRefs` elaborator pass. 
    Based on the design of `ResolvePortRefs`, this is a thing that (we think) 
    is not possible. """

    @h.module
    class I:
        s = h.Port()

    @h.module
    class M:
        s = h.Signal()
        i1 = I(s=s)
        i2 = I(s=s)
        i3 = I(s=i1.s)
        i4 = I(s=i2.s)

    h.elaborate(M)

    # Check this resolved to a single Signal
    assert len(M.signals) == 1
    assert len(M.bundles) == 0
    assert len(M.instances) == 4

    # And check that Signal is connected to all four Instances
    assert M.i1.s is M.s
    assert M.i2.s is M.s
    assert M.i3.s is M.s
    assert M.i4.s is M.s


def test_bad_conns():
    """ Test the errors produced by elaborating with invalid Port connections """

    @h.module
    class I:
        p = h.Port()

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a, b=b, p=c)  # Two of these 3 ports don't exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Connections to invalid Ports" in str(e.value)

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a, b=b)  # None of these ports exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Missing connection to" in str(e.value)

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a, p=b)  # One of these ports don't exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Connection to invalid Port" in str(e.value)

    @h.module
    class O:
        a, b, c = h.Signals(3)
        i = I(a=a)  # All (one) port doesn't exist

    with pytest.raises(RuntimeError) as e:
        h.elaborate(O)
    assert "Missing connection to" in str(e.value)


def test_anon_bundle_refs():
    """ Test adding `BundleRef`s to `AnonymousBundle`s. """

    @h.bundle
    class Diff:
        p, n = h.Signals(2)

    @h.module
    class HasDiff:
        # Module with a `Diff` Port
        d = Diff(port=True)

    @h.module
    class HasHasDiff:
        # Module instantiating a few `HasDiff`
        d = Diff()
        # Instance connected to the Bundle Instance
        h1 = HasDiff(d=d)

        # THE POINT OF THE TEST:
        # Instance with an Anon Bundle, "equal to" the Bundle Instance
        h2 = HasDiff(d=h.AnonymousBundle(p=d.p, n=d.n))
        # Instance with (p, n) flipped
        h3 = HasDiff(d=h.AnonymousBundle(p=d.n, n=d.p))

    h.elaborate(HasHasDiff)


@pytest.mark.xfail(reason="#21 https://github.com/dan-fritchman/Hdl21/issues/21")
def test_generator_port_slice():
    """ Test taking a slice from a Generator `PortRef`. """

    @h.paramclass
    class Width:
        width: h.Param(dtype=int, desc="Width")

    @h.generator
    def SliceMyP(params: Width) -> h.Module:
        m = h.Module()
        m.p = h.Port(width=params.width)  # Port with parametrized width
        return m

    @h.module
    class ScalarPort:
        p = h.Port()  # A width-one port

    @h.module
    class HasGen:
        g = SliceMyP(width=8)()
        # Connect the MSB of `g.p` to `s.p`
        s = ScalarPort(p=g.p[-1])

    h.elaborate(HasGen)


def test_pair1():
    """ Test of the `Diff` and `Pair` signal and instance bundles """
    
    @h.module
    class I:
        ps = h.Port(desc="Port we'll connect to a scalar")
        pd = h.Port(desc="Port we'll connect to a diff")
        pa = h.Port(desc="Port we'll connect to an AnonymousBundle")

    @h.module
    class O:
        d = h.Diff()
        s = h.Signal()
        pair = h.Pair(I)(pd=d, ps=s, pa=h.inverse(d))

    h.elaborate(O)

    assert len(O.instances) == 2
    assert "pair_p" in O.instances
    assert "pair_n" in O.instances
    assert O.pair_p.conns["ps"] is O.s
    assert O.pair_n.conns["ps"] is O.s
    assert O.pair_p.conns["pd"] is O.d_p
    assert O.pair_n.conns["pd"] is O.d_n
    assert O.pair_p.conns["pa"] is O.d_n
    assert O.pair_n.conns["pa"] is O.d_p
    assert len(O.signals) == 3
    assert len(O.bundles) == 0
    assert len(O.instbundles) == 0


@pytest.mark.xfail(reason="#33 https://github.com/dan-fritchman/Hdl21/issues/33")
def test_noconn_types():
    """ Test connecting `NoConn`s to a variety of port-types. """

    @h.module
    class Inner():
        # Inner module with a handful of port-types
        s = h.Port()
        b = h.Port(width=11)
        d = h.Diff(port=True)

    @h.module 
    class Outer:
        i = Inner(s=h.NoConn(), b=h.NoConn(), d=h.NoConn())
    
    h.elaborate(Outer)
