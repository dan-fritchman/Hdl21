import hdl21 as h
from hdl21.sim import *


def test_sim1():
    # Test minimal `Sim` creation
    s = Sim(dut=h.Module(), attrs=[])
    assert isinstance(s, Sim)


def test_sim2():
    """ Test creating a more fully-featured sim """
    Sim(
        dut=h.Module(),
        attrs=[
            Param(name="x", val=5),
            Dc(var="x", sweep=PointSweep([1]), name="mydc"),
            Ac(sweep=LogSweep(1e1, 1e10, 10), name="myac"),
            Tran(tstop=11 * h.units.p, name="mytran"),
            SweepAnalysis(
                inner=[Tran(tstop=1, name="swptran")],
                var="x",
                sweep=LinearSweep(0, 1, 2),
                name="mysweep",
            ),
            MonteCarlo(
                inner=[Dc(var="y", sweep=PointSweep([1]), name="swpdc"),],
                npts=11,
                name="mymc",
            ),
            Save(SaveMode.ALL),
            Meas(analysis="mytr", name="a_delay", expr="trig_targ_something"),
            Include("/home/models"),
            Lib(path="/home/models", section="fast"),
            Options(reltol=1e-9),
        ],
    )


def test_simattrs():
    """ Test the "sim attrs" feature, which adds methods to `Sim` for each `SimAttr` """

    s = Sim(dut=h.Module())

    p = s.param(name="x", val=5)
    dc = s.dc(var=p, sweep=PointSweep([1]), name="mydc")
    ac = s.ac(sweep=LogSweep(1e1, 1e10, 10), name="myac")
    tr = s.tran(tstop=11 * h.units.p, name="mytran")
    sw = s.sweepanalysis(inner=[tr], var=p, sweep=LinearSweep(0, 1, 2), name="mysweep")
    mc = s.montecarlo(
        inner=[Dc(var="y", sweep=PointSweep([1]), name="swpdc"),], npts=11, name="mymc"
    )
    s.save(SaveMode.ALL)
    s.meas(analysis=tr, name="a_delay", expr="trig_targ_something")
    s.include("/home/models")
    s.lib(path="/home/models", section="fast")
    s.options(reltol=1e-9)


def test_tb():
    mytb = tb("mytb")
    assert isinstance(mytb, h.Module)
    assert is_tb(mytb)


def test_proto1():
    s = Sim(
        dut=h.Module(name="tb"),
        attrs=[
            Param(name="x", val=5),
            Dc(var="x", sweep=PointSweep([1]), name="mydc"),
            Ac(sweep=LogSweep(1e1, 1e10, 10), name="myac"),
            Tran(tstop=11 * h.units.p, name="mytran"),
            SweepAnalysis(
                inner=[Tran(tstop=1, name="swptran")],
                var="x",
                sweep=LinearSweep(0, 1, 2),
                name="mysweep",
            ),
            MonteCarlo(
                inner=[Dc(var="y", sweep=PointSweep([1]), name="swpdc"),],
                npts=11,
                name="mymc",
            ),
            Save(SaveMode.ALL),
            Meas(analysis="mytr", name="a_delay", expr="trig_targ_something"),
            Include("/home/models"),
            Lib(path="/home/models", section="fast"),
            Options(reltol=1e-9),
        ],
    )

    to_proto(s)
