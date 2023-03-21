"""
# Test Site

Tests which are only valid with a PDK `install` configured, 
generally via a `sitepdks` package. 
"""

import pytest

# Import the site PDKs, or skip all these tests if not available.
sitepdks = pytest.importorskip("sitepdks")

# If that succeeded, import the PDK we want to test.
# It should have a valid `install` attribute.
import hdl21 as h
import gf180
import vlsirtools.spice as vsp
from .pdk import modules as g


def test_installed():
    assert gf180.install is not None
    assert isinstance(gf180.install, gf180.Install)


def test_sim_components():
    # Test all components
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            for idx, val in enumerate(vars(g).values()):

                exec("comp_" + str(idx) + "=val()")

                for jdx, p in enumerate(val().ports):
                    if jdx == 0:
                        exec("comp_" + str(idx) + "." + p + "=vdd")
                    else:
                        exec("comp_" + str(idx) + "." + p + "=VSS")

        # Simulation Controls
        op = h.sim.Op()
        design_inc = gf180.install.include_design()
        mos_inc = gf180.install.include_mos(h.pdk.Corner.TYP)
        res_inc = gf180.install.include_resistors(h.pdk.Corner.TYP)
        dio_inc = gf180.install.include_diodes(h.pdk.Corner.TYP)
        bjt_inc = gf180.install.include_bjts(h.pdk.Corner.TYP)
        mimcap_inc = gf180.install.include_mimcaps(h.pdk.Corner.TYP)
        moscap_inc = gf180.install.include_moscaps(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)
