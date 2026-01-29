"""
# Test Site Simulations

Tests IHP PDK components with default include statements
to ensure simulators are functioning as intended.

These tests require:
1. A valid IHP-Open-PDK installation
2. The sitepdks module configured with ihp_hdl21.install
3. ngspice or xyce simulator available
"""

import pytest

# Import the site PDKs, or skip all these tests if not available.
sitepdks = pytest.importorskip("sitepdks")

# If that succeeded, import the PDK we want to test.
# It should have a valid `install` attribute.
import ihp_hdl21 as ihp
import hdl21 as h
import vlsirtools.spice as vsp
import ihp_hdl21.primitives as s


def test_installed():
    """
    Test if the PDK is installed and properly configured.

    This test checks if the PDK `ihp.install` is not None and if its type
    is `ihp.Install`. If both conditions are met, the test passes.
    """
    assert ihp.install is not None
    assert isinstance(ihp.install, ihp.Install)


def test_sim():
    """
    Test the DC operating point simulation of a single LV NMOS transistor.

    This test creates a simple testbench with a single LV NMOS transistor,
    runs a DC operating point simulation, and checks if the output current
    falls within a specific range.
    """

    @h.sim.sim
    class Sim:
        """Single transistor simulation"""

        @h.module
        class Tb:  # Testbench
            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1.2)(p=vdd, n=VSS)
            n = ihp.primitives.LV_NMOS(ihp.IhpMosParams(w=1.0, l=0.13))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )

        # Simulation Controls
        op = h.sim.Op()
        inc_lv = ihp.install.include_mos_lv(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )
    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_inv():
    """
    Test the DC operating point simulation of a default-sized inverter.

    This test creates a testbench with a default-sized LV inverter, runs a
    DC operating point simulation, and checks if the output voltage falls
    within the expected range around VDD/2.
    """

    @h.module
    class Inv:  # Default-sized inverter
        i, o, VDD, VSS = 4 * h.Port()
        n = ihp.primitives.LV_NMOS(ihp.IhpMosParams(w=0.5, l=0.13))(
            d=o, g=i, s=VSS, b=VSS
        )
        p = ihp.primitives.LV_PMOS(ihp.IhpMosParams(w=1.0, l=0.13))(
            d=o, g=i, s=VDD, b=VDD
        )

    @h.sim.sim
    class Sim:
        """# Inverter DC OP Simulation"""

        @h.module
        class Tb:  # Testbench
            VSS = h.Port()
            s, VDD = 2 * h.Signal()
            vvdd = h.Vdc(dc=1.2)(p=VDD, n=VSS)
            inv = Inv(i=s, o=s, VDD=VDD, VSS=VSS)

        # Simulation Controls
        op = h.sim.Op()
        inc = ihp.install.include_mos_lv(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )
    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)
    # When input = output (self-biased), voltage should be around VDD/2
    vs = op.data["v(xtop.s)"]
    assert vs > 0.4
    assert vs < 0.8


def test_sim_mosfets_lv():
    """
    Test simulation of all LV MOS transistors.
    """

    @h.sim.sim
    class Sim:
        @h.module
        class Tb:
            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1.2)(p=vdd, n=VSS)

            p = ihp.IhpMosParams

            lv_nmos = s.LV_NMOS(p(w=0.35, l=0.13))(d=vdd, g=vdd, s=VSS, b=VSS)
            lv_pmos = s.LV_PMOS(p(w=0.35, l=0.13))(d=vdd, g=VSS, s=vdd, b=vdd)

        # Simulation Controls
        op = h.sim.Op()
        inc = ihp.install.include_mos_lv(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_mosfets_hv():
    """
    Test simulation of all HV MOS transistors.
    """

    @h.sim.sim
    class Sim:
        @h.module
        class Tb:
            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=3.3)(p=vdd, n=VSS)

            q = ihp.IhpMosHvParams

            hv_nmos = s.HV_NMOS(q(w=0.35, l=0.45))(d=vdd, g=vdd, s=VSS, b=VSS)
            hv_pmos = s.HV_PMOS(q(w=0.35, l=0.45))(d=vdd, g=VSS, s=vdd, b=vdd)

        # Simulation Controls
        op = h.sim.Op()
        inc = ihp.install.include_mos_hv(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_resistors():
    """
    Test simulation of IHP resistors.
    """

    @h.sim.sim
    class Sim:
        @h.module
        class Tb:
            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1.2)(p=vdd, n=VSS)

            p = ihp.IhpResParams()

            # 3-terminal resistors (p, n, b)
            res_rsil = s.RSIL(p)(p=VSS, n=vdd, b=VSS)
            res_rhigh = s.RHIGH(p)(p=VSS, n=vdd, b=VSS)
            res_rppd = s.RPPD(p)(p=VSS, n=vdd, b=VSS)

        # Simulation Controls
        op = h.sim.Op()
        inc_lv = ihp.install.include_mos_lv(h.pdk.Corner.TYP)
        inc_res = ihp.install.include_res(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_capacitors():
    """
    Test simulation of IHP MIM capacitors.
    """

    @h.sim.sim
    class Sim:
        @h.module
        class Tb:
            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1.2)(p=vdd, n=VSS)

            p = ihp.IhpCapParams()

            # MIM capacitor (2-terminal)
            cap_cmim = s.CAP_CMIM(p)(p=vdd, n=VSS)
            # RF MIM capacitor (3-terminal)
            cap_rfcmim = s.CAP_RFCMIM(p)(p=vdd, n=VSS, b=VSS)

        # Simulation Controls
        op = h.sim.Op()
        inc_lv = ihp.install.include_mos_lv(h.pdk.Corner.TYP)
        inc_cap = ihp.install.include_cap(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_hbt():
    """
    Test simulation of IHP HBT transistors.

    IHP's SiGe HBTs are the highlight of this technology,
    offering exceptional RF performance (fT up to 350 GHz).
    """

    @h.sim.sim
    class Sim:
        @h.module
        class Tb:
            VSS = h.Port()
            vcc = h.Signal()
            vb = h.Signal()
            v = h.Vdc(dc=3.3)(p=vcc, n=VSS)
            vbias = h.Vdc(dc=0.9)(p=vb, n=VSS)

            p = ihp.IhpHbtParams()

            # Standard HBT (4-terminal: c, b, e, bn)
            npn13g2 = s.NPN13G2(p)(c=vcc, b=vb, e=VSS, bn=VSS)
            # Large HBT
            npn13g2l = s.NPN13G2L(p)(c=vcc, b=vb, e=VSS, bn=VSS)
            # Variable emitter HBT
            npn13g2v = s.NPN13G2V(p)(c=vcc, b=vb, e=VSS, bn=VSS)

        # Simulation Controls
        op = h.sim.Op()
        inc_hbt = ihp.install.include_hbt(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_pnp():
    """
    Test simulation of IHP lateral PNP transistor.
    """

    @h.sim.sim
    class Sim:
        @h.module
        class Tb:
            VSS = h.Port()
            vcc = h.Signal()
            vb = h.Signal()
            v = h.Vdc(dc=3.3)(p=vcc, n=VSS)
            vbias = h.Vdc(dc=2.5)(p=vb, n=VSS)

            p = ihp.IhpPnpParams()

            # Lateral PNP (3-terminal: c, b, e)
            pnp = s.PNPMPA(p)(c=VSS, b=vb, e=vcc)

        # Simulation Controls
        op = h.sim.Op()
        inc_hbt = ihp.install.include_hbt(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_transient():
    """
    Test a transient simulation of an inverter ring oscillator.
    """

    @h.module
    class Inv:
        i, o, VDD, VSS = 4 * h.Port()
        n = ihp.primitives.LV_NMOS(ihp.IhpMosParams(w=0.5, l=0.13))(
            d=o, g=i, s=VSS, b=VSS
        )
        p = ihp.primitives.LV_PMOS(ihp.IhpMosParams(w=1.0, l=0.13))(
            d=o, g=i, s=VDD, b=VDD
        )

    @h.module
    class RingOsc3:
        """3-stage ring oscillator"""

        VDD, VSS = 2 * h.Port()
        out = h.Port()
        n1, n2 = 2 * h.Signal()

        inv1 = Inv(i=out, o=n1, VDD=VDD, VSS=VSS)
        inv2 = Inv(i=n1, o=n2, VDD=VDD, VSS=VSS)
        inv3 = Inv(i=n2, o=out, VDD=VDD, VSS=VSS)

    @h.sim.sim
    class Sim:
        @h.module
        class Tb:
            VSS = h.Port()
            VDD, out = 2 * h.Signal()
            vvdd = h.Vdc(dc=1.2)(p=VDD, n=VSS)
            ring = RingOsc3(VDD=VDD, VSS=VSS, out=out)

        # Simulation Controls
        tr = h.sim.Tran(tstop=10e-9, tstep=1e-12)
        inc = ihp.install.include_mos_lv(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    tr = rv[vsp.sim_data.AnalysisType.TRAN]
    assert isinstance(tr, vsp.sim_data.TranResult)
