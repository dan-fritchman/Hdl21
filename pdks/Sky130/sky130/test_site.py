"""
# Test Site

Tests which are only valid with a PDK `install` configured, 
generally via a `sitepdks` package. 
"""

import pytest

# Import the site PDKs, or skip all these tests if not available.
sitepdks = pytest.importorskip("sitepdks")
if not hasattr(sitepdks, "sky130"):
    pytest.skip("No sky130 PDK install configured", allow_module_level=True)

# If that succeeded, import the PDK we want to test.
# It should have a valid `install` attribute.
import sky130
import hdl21 as h
import vlsirtools.spice as vsp


def test_installed():
    assert sky130.install is not None
    assert isinstance(sky130.install, sky130.Install)


def test_sim():
    """# Test invoking simulation"""

    @h.sim.sim
    class Sim:
        """Single transistor simulation"""

        @h.module
        class Tb:  # Testbench
            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)
            n = sky130.modules.sky130_fd_pr__nfet_01v8()(d=vdd, g=vdd, s=VSS, b=VSS)

        # Simulation Controls
        op = h.sim.Op()
        inc = sky130.install.include(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )
    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)
    id = abs(op.data["i(v.xtop.vv)"])
    assert id > 5e-5
    assert id < 6e-5


def test_sim_inv():
    """# Test invoking simulation on a default inverter"""

    @h.module
    class Inv:  # Default-sized inverter
        i, o, VDD, VSS = 4 * h.Port()
        n = sky130.modules.sky130_fd_pr__nfet_01v8()(d=o, g=i, s=VSS, b=VSS)
        p = sky130.modules.sky130_fd_pr__pfet_01v8()(d=o, g=i, s=VDD, b=VDD)

    @h.sim.sim
    class Sim:
        """# Inverter DC OP Simulation"""

        @h.module
        class Tb:  # Testbench
            VSS = h.Port()
            s, VDD = 2 * h.Signal()
            vvdd = h.Vdc(dc=1)(p=VDD, n=VSS)
            inv = Inv(i=s, o=s, VDD=VDD, VSS=VSS)

        # Simulation Controls
        op = h.sim.Op()
        inc = h.sim.Lib(path=sky130.install.model_lib, section="tt")

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )
    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)
    vs = op.data["v(xtop.s)"]
    assert vs > 0.5
    assert vs < 0.55
