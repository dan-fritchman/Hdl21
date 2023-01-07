"""
# Hdl21 Unit Tests

Not necessarily exclusive to `Bundle`s, but focusing on them.
"""
import copy, pytest
from enum import Enum, EnumMeta, auto

import hdl21 as h


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
    assert "i1_i" not in m3.namespace

    # First run the "implicit bundles" pass, and see that an explicit one is created
    from hdl21.elab import ElabPass

    m3 = h.elaborate(m3, passes=[ElabPass.RESOLVE_PORT_REFS])
    assert isinstance(m3, h.Module)
    assert isinstance(m3.i1, h.Instance)
    assert isinstance(m3.i2, h.Instance)
    assert "i1_i" in m3.namespace

    # Now elaborate it the rest of the way, to scalar signals
    m3 = h.elaborate(m3)
    assert "i1_i" not in m3.namespace
    assert "i1_i_s" in m3.namespace
    assert isinstance(m3.get("i1_i_s"), h.Signal)
    assert m3.get("i1_i_s") in m3.i1.conns.values()


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
    assert "host_hr" not in System.namespace

    # First run the "implicit bundles" pass, and see that an explicit one is created
    from hdl21.elab import ElabPass

    sys = h.elaborate(System, passes=[ElabPass.RESOLVE_PORT_REFS])
    assert "host_hr" in sys.namespace

    # Now expand the rest of the way, down to scalar signals
    # Check that bundle went away, and its constituent signals replaced it
    sys = h.elaborate(sys)
    assert "host_hr" not in sys.namespace
    assert "host_hr_tx" in sys.namespace
    assert "host_hr_rx" in sys.namespace
    assert "host_hr_txd_p" in sys.namespace
    assert "host_hr_txd_n" in sys.namespace
    assert "host_hr_rxd_p" in sys.namespace
    assert "host_hr_rxd_n" in sys.namespace


def test_bigger_bundles():
    """Test a slightly more elaborate Bundle-based system"""

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
    assert Board.get("chip_spi_sck").vis == h.signal.Visibility.INTERNAL
    assert Board.get("chip_spi_cs").vis == h.signal.Visibility.INTERNAL
    assert Board.get("chip_spi_dq").vis == h.signal.Visibility.INTERNAL

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


def test_bad_bundle_conn():
    """Test invalid Bundle connections"""

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


def test_copy_bundle_instance():
    """Copying a BundleInstance"""
    # This generally fails when run in the debugger, but seems alright stand-alone (?)
    copy.copy(h.BundleInstance(name="inst", of=h.Bundle()))


def test_bundle_destructure():
    """Test de-structuring bundles to individual Signals"""

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


def test_sub_bundle_conn():
    """Test connecting via BundleRef to a sub-Bundle"""

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
        hasb1 = HasB1(b1=b2.b1)

    h.elaborate(HasB2)


def test_nested_bundle_conn():
    """Test connecting to a nested bundle ref"""

    @h.bundle
    class B1:
        s = h.Signal()

    @h.bundle
    class B2:
        b1 = B1()

    @h.bundle
    class B3:
        b2 = B2()

    @h.bundle
    class B4:
        b3 = B3()

    @h.module
    class HasB1:
        b1 = B1(port=True)

    @h.module
    class HasB4:
        b4 = B4()
        hasb1 = HasB1(b1=b4.b3.b2.b1)

    h.elaborate(HasB4)


def test_nested_bundle_conn2():
    """Test some bundles which have multiple instances of the same bundle as attributes."""

    @h.bundle
    class Ab:
        a, b = h.Signals(2)

    @h.bundle
    class FourAbs:
        i0 = Ab()
        i1 = Ab()
        i2 = Ab()
        i3 = Ab()

    @h.module
    class HasAbPort:
        ab = Ab(port=True)

    @h.module
    class HasThose:
        four_abs = FourAbs()
        i0 = HasAbPort(ab=four_abs.i0)
        i1 = HasAbPort(ab=four_abs.i1)
        i2 = HasAbPort(ab=four_abs.i2)
        i3 = HasAbPort(ab=four_abs.i3)

    h.elaborate(HasThose)

    assert HasThose.instances["i0"].conns["ab_a"].name == "four_abs_i0_a"
    assert HasThose.instances["i0"].conns["ab_b"].name == "four_abs_i0_b"
    assert HasThose.instances["i1"].conns["ab_a"].name == "four_abs_i1_a"
    assert HasThose.instances["i1"].conns["ab_b"].name == "four_abs_i1_b"
    assert HasThose.instances["i2"].conns["ab_a"].name == "four_abs_i2_a"
    assert HasThose.instances["i2"].conns["ab_b"].name == "four_abs_i2_b"
    assert HasThose.instances["i3"].conns["ab_a"].name == "four_abs_i3_a"
    assert HasThose.instances["i3"].conns["ab_b"].name == "four_abs_i3_b"


def test_anon_bundle_port_conn():
    """Test connecting via PortRef to an AnonymousBundle"""

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


def test_anon_bundle_refs():
    """Test adding `BundleRef`s to `AnonymousBundle`s."""

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


@pytest.mark.xfail(reason="#68 https://github.com/dan-fritchman/Hdl21/issues/68")
def test_no_role_directions():
    """Test directions on Bundles without Roles"""

    @h.bundle
    class B:
        # A Bundle with directed Ports
        a = h.Input()
        b = h.Output()
        c = h.Inout()
        d = h.Port()
        e = h.Signal()

    @h.module
    class HasB:
        b = B(port=True)

    @h.module
    class HasHasB:
        b = B()
        h1 = HasB(b=b)

    h.elaborate(HasHasB)

    assert HasB.b_a.direction == h.PortDir.INPUT
    assert HasB.b_b.direction == h.PortDir.OUTPUT
    assert HasB.b_c.direction == h.PortDir.INPUT
    assert HasB.b_d.direction == h.PortDir.NONE
    assert HasB.b_e.direction == None


def test_re_elab_generator_with_bundle_portref():
    """Test re-elaborating a generator with a bundle port, and a `PortRef` to it.
    This can be problematic as bundle ports are flattened during elaboration."""

    @h.generator
    def G(_: h.HasNoParams) -> h.Module:
        @h.module
        class G:
            p = h.Diff(port=True)

        return G

    @h.generator
    def T(_: h.HasNoParams) -> h.Module:
        @h.module
        class T:
            g1 = G()()
            g2 = G()(p=g1.p)

        return T

    h.elaborate(T())
    h.elaborate(T())


def test_re_elab_bundle_port():
    """Test elaborating, then re-elaborating Modules with Bundle-ports."""

    @h.bundle
    class Ab:
        a, b = h.Signals(2)

    @h.module
    class Bot:
        ab = Ab(port=True)

    @h.module
    class Top1:
        ab = Ab()
        bot = Bot(ab=ab)

    # Elaborate `Top1`. This works just fine.
    h.elaborate(Top1)

    # Now the problem children
    @h.module
    class Top2:
        ab = Ab()
        bot = Bot(ab=ab)  # <= especially this here

    # Elaborating `Top2` fails, as `Bot`'s bundle-valued ports have been flattened
    h.elaborate(Top2)


def test_bundle_noconns():
    """Test connecting `NoConn` to bundle-valued ports"""

    @h.bundle
    class A:
        ...  # empty

    @h.bundle
    class B:
        s1 = h.Signal()

    @h.bundle
    class C:
        s1, s2, s3 = h.Signals(3)

    @h.module
    class Bot:
        a = A(port=True)
        b = B(port=True)
        c = C(port=True)

    @h.module
    class Top:
        bot1 = Bot(
            a=h.NoConn(),
            b=h.NoConn(),
            c=h.NoConn(),
        )

    # Add another instance procedurally, and connect it via PortRefs
    Top.bot2 = Bot()
    Top.bot2.a = h.NoConn()
    Top.bot2.b = h.NoConn()
    Top.bot2.c = h.NoConn()

    # Elaborate it, flesh all this out
    h.elaborate(Top)

    assert len(Bot.ports) == 4
    assert sorted(Bot.ports.keys()) == [
        "b_s1",
        "c_s1",
        "c_s2",
        "c_s3",
    ]
    assert len(Top.signals) == 8
    assert sorted(Top.signals.keys()) == [
        "bot1_b_s1",
        "bot1_c_s1",
        "bot1_c_s2",
        "bot1_c_s3",
        "bot2_b_s1",
        "bot2_c_s1",
        "bot2_c_s2",
        "bot2_c_s3",
    ]

    assert Top.bot1.conns["b_s1"] is Top.bot1_b_s1
    assert Top.bot1.conns["c_s1"] is Top.bot1_c_s1
    assert Top.bot1.conns["c_s2"] is Top.bot1_c_s2
    assert Top.bot1.conns["c_s3"] is Top.bot1_c_s3

    assert Top.bot2.conns["b_s1"] is Top.bot2_b_s1
    assert Top.bot2.conns["c_s1"] is Top.bot2_c_s1
    assert Top.bot2.conns["c_s2"] is Top.bot2_c_s2
    assert Top.bot2.conns["c_s3"] is Top.bot2_c_s3
