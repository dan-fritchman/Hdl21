"""
# `hdl21.sim` Unit Tests
"""

import pytest

import hdl21 as h
from hdl21.sim import *
from hdl21.prefix import m
from hdl21.primitives import Vdc
import vlsir.spice_pb2 as vsp
import vlsirtools
from vlsirtools.spice import sim, SimOptions, ResultFormat, sim_data as sd


def test_sim1():
    """Test minimal `Sim` creation"""
    s = Sim(tb=tb("empty"), attrs=[])
    assert isinstance(s, Sim)
    assert s.tb.name == "empty"
    assert len(s.tb.ports) == 1
    assert s.attrs == []


@h.module
class MyTb:
    # Create a sample testbench, particularly with enough stuff in it for `Noise` analysis.
    # I.e. a source instance and a non-ground Signal.
    VSS = h.Port()
    p = h.Signal()
    v = Vdc(dc=0 * m, ac=1000 * m)(p=p, n=VSS)


def test_sim2():
    """Test creating a more fully-featured sim"""
    s = Sim(
        tb=MyTb,
        attrs=[
            Param(name="x", val=5),
            Dc(var="x", sweep=PointSweep([1]), name="mydc"),
            Ac(sweep=LogSweep(1e1, 1e10, 10), name="myac"),
            Tran(tstop=11 * h.prefix.p, name="mytran"),
            Noise(
                output=MyTb.p,
                input_source=MyTb.v,
                sweep=LogSweep(1e1, 1e10, 10),
                name="mynoise",
            ),
            SweepAnalysis(
                inner=[Tran(tstop=1, name="swptran")],
                var="x",
                sweep=LinearSweep(0, 1, 2),
                name="mysweep",
            ),
            MonteCarlo(
                inner=[
                    Dc(var="y", sweep=PointSweep([1]), name="swpdc"),
                ],
                npts=11,
                name="mymc",
            ),
            Save(SaveMode.ALL),
            Meas(analysis="mytr", name="a_delay", expr="trig_targ_something"),
            Include("/home/models"),
            Lib(path="/home/models", section="fast"),
            Options(1e-9, name="reltol"),
        ],
    )
    to_proto(s)


def test_simattrs():
    """Test the "sim attrs" feature, which adds methods to `Sim` for each `SimAttr`"""

    s = Sim(tb=MyTb)

    p = s.param(name="x", val=5)
    dc = s.dc(var=p, sweep=PointSweep([1]), name="mydc")
    ac = s.ac(sweep=LogSweep(1e1, 1e10, 10), name="myac")
    tr = s.tran(tstop=11 * h.prefix.p, name="mytran")
    noise = s.noise(
        output=MyTb.p,
        input_source=MyTb.v,
        sweep=LogSweep(1e1, 1e10, 10),
        name="mynoise",
    )
    assert tr.tstop == 11 * h.prefix.p
    sw = s.sweepanalysis(inner=[tr], var=p, sweep=LinearSweep(0, 1, 2), name="mysweep")
    mc = s.montecarlo(
        inner=[
            Dc(var="y", sweep=PointSweep([1]), name="swpdc"),
        ],
        npts=11,
        name="mymc",
    )
    s.save(SaveMode.ALL)
    s.meas(analysis=tr, name="a_delay", expr="trig_targ_something")
    s.include("/home/models")
    s.lib(path="/home/models", section="fast")
    s.options(1e-9, name="reltol")

    to_proto(s)


def test_sim_decorator():
    """Test creating the same Sim, via the class decorator"""

    @h.sim.sim
    class MySim:
        tb = MyTb

        x = Param(5)
        y = Param(6)
        mydc = Dc(var=x, sweep=PointSweep([1]))
        myac = Ac(sweep=LogSweep(1e1, 1e10, 10))
        mytran = Tran(tstop=11 * h.prefix.p)
        mynoise = Noise(
            output=MyTb.p,
            input_source=MyTb.v,
            sweep=LogSweep(1e1, 1e10, 10),
        )
        mysweep = SweepAnalysis(
            inner=[mytran],
            var=x,
            sweep=LinearSweep(0, 1, 2),
        )
        mymc = MonteCarlo(
            inner=[
                Dc(var="y", sweep=PointSweep([1]), name="swpdc"),
            ],
            npts=11,
        )
        a_delay = Meas(analysis=mytran, expr="trig_targ_something")
        opts = Options(1e-9, name="reltol")

        # Attributes whose names don't really matter can be called anything,
        # but must be *assigned* into the class, not just constructed.
        _ = Save(SaveMode.ALL)

        # The `a_path` field will be dropped from the `Sim` definition,
        # but can be referred to by the following attributes.
        a_path = "/home/models"
        _ = Include(a_path)
        _ = Lib(path=a_path, section="fast")

    assert isinstance(MySim, Sim)
    assert MySim.name == "MySim"
    assert isinstance(MySim.tb, h.Module)
    assert MySim.tb.name == "MyTb"
    assert isinstance(MySim.attrs, list)
    for attr in MySim.attrs:
        assert is_simattr(attr)
    assert not hasattr(MySim, "a_path")

    to_proto(MySim)


def test_tb():
    """Test the `tb` function"""
    mytb = tb("mytb")
    assert isinstance(mytb, h.Module)
    assert is_tb(mytb)
    assert len(mytb.ports) == 1


def test_proto1():
    """Test exporting `Sim` to the VLSIR Protobuf schema"""

    s = Sim(
        tb=MyTb,
        attrs=[
            Param(name="x", val=5),
            Dc(var="x", sweep=PointSweep([1]), name="mydc"),
            Ac(sweep=LogSweep(1e1, 1e10, 10), name="myac"),
            Tran(tstop=11 * h.prefix.p, name="mytran"),
            SweepAnalysis(
                inner=[Tran(tstop=1, name="swptran")],
                var="x",
                sweep=LinearSweep(0, 1, 2),
                name="mysweep",
            ),
            MonteCarlo(
                inner=[
                    Dc(var="y", sweep=PointSweep([1]), name="swpdc"),
                ],
                npts=11,
                name="mymc",
            ),
            Save(SaveMode.ALL),
            Meas(analysis="mytr", name="a_delay", expr="trig_targ_something"),
            Include("/home/models"),
            Lib(path="/home/models", section="fast"),
            Options(1e-9, name="reltol"),
        ],
    )

    p = to_proto(s)

    import vlsir.circuit_pb2 as vckt
    import vlsir.spice_pb2 as vsp

    assert isinstance(p.pkg, vckt.Package)
    assert p.top == "test_sim.MyTb"


def test_generator_sim():
    """Test creating and exporting `Sim` with generator-valued DUTs,
    particularly several with different parameter-values."""

    @h.paramclass
    class P:  # A largely dummy param-class
        i = h.Param(dtype=int, desc="An integer", default=11)

    @h.generator
    def G(p: P) -> h.Module:
        m = h.Module()
        m.VSS = h.Port()
        return m

    # Create a few instances
    g1 = G(P(1))
    g2 = G(P(2))

    # Create `Sim`s of them
    s1 = Sim(tb=g1)
    s2 = Sim(tb=g2)

    # And export both to protobuf
    p1 = to_proto(s1)
    p2 = to_proto(s2)

    assert p1.top != p2.top
    assert p1.top == "test_sim.G(i=1)"
    assert p2.top == "test_sim.G(i=2)"


def test_delay1():
    from hdl21.sim import delay
    from hdl21.sim.delay import DelaySimParams, LogicState, Transition
    from hdl21.prefix import p, n, f, m

    @h.module
    class M:
        i0, i1 = h.Inputs(2)
        o0, o1 = h.Outputs(2)
        vdd, vss = h.Ports(2)

    p = DelaySimParams(
        dut=M,
        primary_input=M.i0,
        other_inputs=dict(i1=LogicState.HIGH),
        input_trans=Transition.RISING,
        vlo=0 * m,
        vhi=1000 * m,
        supplies=dict(vdd=1000 * m),
        grounds=[M.vss],
        load_caps=dict(o0=2 * f),
        default_load_cap=1 * f,
        tstop=1 * n,
        tstep=1 * p,
        pathsep=":",
    )
    delay_sim = delay.create_sim(p)
    h.sim.to_proto(delay_sim)
    # FIXME! some real checks plz


def empty_tb(num=0) -> h.Module:
    from hdl21.prefix import K
    from hdl21.primitives import R

    ri = R(R.Params(r=1 * K))

    @h.module
    class EmptyTb:
        """An Empty TestBench,
        or as close as we can get to one without some simulators failing.
        AKA, a resistor to ground."""

        VSS = h.Port()
        s = h.Signal()
        r = ri(p=s, n=VSS)

    EmptyTb.name = f"EmptyTb{num}"
    return EmptyTb


@pytest.mark.skipif(
    vlsirtools.spice.default() is None,
    reason="No simulator available",
)
def test_empty_sim1():
    """Create and run an empty `Sim`, returning a VLSIR_PROTO"""

    s = Sim(tb=empty_tb(), attrs=[])
    r = sim(to_proto(s), SimOptions(fmt=ResultFormat.VLSIR_PROTO))
    assert isinstance(r, vsp.SimResult)
    assert not len(r.an)  # No analysis inputs, no analysis results


@pytest.mark.skipif(
    vlsirtools.spice.default() is None,
    reason="No simulator available",
)
@pytest.mark.skipif(
    vlsirtools.spice.default() == vlsirtools.spice.SupportedSimulators.XYCE,
    reason="No support for `Xyce` + `SimData` python types",
)
def test_empty_sim2():
    """Create and run an empty `Sim`, returning SIM_DATA"""

    s = Sim(tb=empty_tb(), attrs=[])
    r = sim(to_proto(s), SimOptions(fmt=ResultFormat.SIM_DATA))
    assert isinstance(r, sd.SimResult)
    assert not len(r.an)  # No analysis inputs, no analysis results


@pytest.mark.xfail(reason="VLSIR #71 https://github.com/Vlsir/Vlsir/issues/71")
def test_multi_sim():
    """Test multiple Sims in parallel"""
    s1 = Sim(tb=empty_tb(1), attrs=[])
    s2 = Sim(tb=empty_tb(2), attrs=[])
    s3 = Sim(tb=empty_tb(3), attrs=[])
    s4 = Sim(tb=empty_tb(4), attrs=[])

    r = sim(to_proto([s1, s2, s3, s4]), SimOptions(fmt=ResultFormat.VLSIR_PROTO))

    for a in r:
        assert isinstance(a, vsp.SimResult)
        assert not len(a.an)


def really_empty_tb() -> h.Module:
    @h.module
    class ReallyEmptyTb:
        """An Empty TestBench, this time REALLY empty.
        For inducing an error in a multi-sim below."""

    return ReallyEmptyTb


def test_multi_sim_error():
    """Test that a failure in multiple concurrent sims fails, unlike in erdewit/nest_asyncio#57"""
    with pytest.raises(Exception):
        s1 = Sim(tb=empty_tb(1), attrs=[])
        s2 = Sim(tb=really_empty_tb(), attrs=[])
        s3 = Sim(tb=empty_tb(3), attrs=[])
        s4 = Sim(tb=empty_tb(4), attrs=[])

        r = sim(to_proto([s1, s2, s3, s4]), SimOptions(fmt=ResultFormat.VLSIR_PROTO))
