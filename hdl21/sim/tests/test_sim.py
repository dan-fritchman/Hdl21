import hdl21 as h
from hdl21 import sim


def test_sim1():
    sim.Sim(dut=h.Module(), attrs=[])


def test_sim2():
    sim.Sim(
        dut=h.Module(),
        attrs=[
            sim.Dc(name="dc1", var="FIXME", sweep=sim.PointSweep((1, 2, 3))),
            sim.Tran(name="tran1", tstop=1e-12),
            sim.Ac(name="ac1", sweep=sim.LogSweep(0, 10, 100)),
        ],
    )
