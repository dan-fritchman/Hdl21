"""
# Test Site Simulations

Tests all PDK components with default include statements
to ensure simulators are functioning as intended.
"""

import pytest

# Import the site PDKs, or skip all these tests if not available.
sitepdks = pytest.importorskip("sitepdks")

# If that succeeded, import the PDK we want to test.
# It should have a valid `install` attribute.
import sky130_hdl21 as sky130
import hdl21 as h
import vlsirtools.spice as vsp
import sky130_hdl21.primitives as s


def test_installed():
    """
    Test if the PDK is installed and properly configured.

    This test checks if the PDK `sky130.install` is not None and if its type
    is `sky130.Install`. If both conditions are met, the test passes.
    """
    assert sky130.install is not None
    assert isinstance(sky130.install, sky130.Install)


def test_sim():
    """
    Test the DC operating point simulation of a single transistor.

    This test creates a simple testbench with a single NMOS transistor, runs a DC operating point
    simulation, and checks if the output current falls within a specific range. If the output current
    is within the specified range, the test passes.
    """

    @h.sim.sim
    class Sim:
        """Single transistor simulation"""

        @h.module
        class Tb:  # Testbench
            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)
            n = sky130.primitives.NMOS_1p8V_STD()(d=vdd, g=vdd, s=VSS, b=VSS)

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
    """
    Test the DC operating point simulation of a default-sized inverter.

    This test creates a testbench with a default-sized inverter, runs a DC operating point
    simulation, and checks if the output voltage falls within a specific range. If the output voltage
    is within the specified range, the test passes.
    """

    @h.module
    class Inv:  # Default-sized inverter
        i, o, VDD, VSS = 4 * h.Port()
        n = sky130.primitives.NMOS_1p8V_STD()(d=o, g=i, s=VSS, b=VSS)
        p = sky130.primitives.PMOS_1p8V_STD()(d=o, g=i, s=VDD, b=VDD)

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
    vs = op.data["v(xtop.s)"]
    assert vs > 0.5
    assert vs < 0.55


def test_sim_mosfets():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = sky130.Sky130MosParams
            q = sky130.Sky130Mos20VParams

            nfet_01v8 = s.NMOS_1p8V_STD(p(w=0.420, l=0.150))(d=vdd, g=vdd, s=VSS, b=VSS)
            nfet_01v8_lvt = s.NMOS_1p8V_LOW(p(w=0.420, l=0.150))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            pfet_01v8 = s.PMOS_1p8V_STD(p(w=0.550, l=0.150))(d=vdd, g=vdd, s=VSS, b=VSS)
            pfet_01v8_hvt = s.PMOS_1p8V_HIGH(p(w=0.550, l=0.150))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            pfet_01v8_lvt = s.PMOS_1p8V_LOW(p(w=0.550, l=0.350))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            pfet_g5v0d10v5 = s.PMOS_5p5V_D10_STD(p(w=0.420, l=0.500))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            nfet_g5v0d10v5 = s.NMOS_5p5V_D10_STD(p(w=0.420, l=0.500))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            pfet_g5v0d16v0 = s.PMOS_5p5V_D16_STD(p(w=5.000, l=0.660))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )

            # This weirdo needs 5 terminals
            nfet_20v0_iso = s.NMOS_ISO_20p0V(q(w=30.000, l=1.500))(
                d=vdd, g=vdd, s=VSS, b=VSS, sub=VSS
            )

            # 20V series only accepts W/L/m
            pfet_20v0 = s.PMOS_20p0V(q(w=30, l=1, m=1))(d=vdd, g=vdd, s=VSS, b=VSS)
            nfet_20v0_zvt = s.NMOS_20p0V_LOW(q(w=30.000, l=1.500))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            nfet_20v0 = s.NMOS_20p0V_STD(q(w=29.410, l=2.950))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            nfet_20v0_nvt = s.NMOS_20p0V_NAT(q(w=30.000, l=1.000))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )

            nfet_03v3_nvt = s.NMOS_3p3V_NAT(p(w=0.700, l=0.500))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            nfet_05v0_nvt = s.NMOS_5p0V_NAT(p(w=0.700, l=0.900))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            esd_nfet_01v8 = s.ESD_NMOS_1p8V(p(w=20.350, l=0.165))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )

            # ESD G5V0D10V5's are simply unavailable in the high-level SPICE libraries in the PDK!
            # esd_nfet_g5v0d10v5_nvt = s.ESD_NMOS_5p5V_NAT(p(w = 10.000, l = 0.900))(d=vdd, g=vdd, s=VSS, b=VSS)
            # esd_nfet_g5v0d10v5 = s.ESD_NMOS_5p5V_D10(p(w = 14.500, l = 0.550))(d=vdd, g=vdd, s=VSS, b=VSS)
            # esd_pfet_g5v0d10v5 = s.ESD_PMOS_5p5V(p(w = 14.500, l = 0.550))(d=vdd, g=vdd, s=VSS, b=VSS)

        # Simulation Controls
        op = h.sim.Op()
        # wnf = h.sim.Options(wnflag=1)
        mc_mm_switch = h.sim.Param(0)
        mc_pr_switch = h.sim.Param(0)
        i1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt.spice"
        )
        i2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical.spice"
        )
        i3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical__lin.spice"
        )
        i4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/specialized_cells.spice"
        )
        # inc = sky130.install.include(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_genres():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = sky130.Sky130GenResParams()

            res_gen_po = s.GEN_PO(p)(p=VSS, n=vdd)

            # FIXME: These models will only simulate in ngspice
            # with a name starting with "R" (why? why not!)

            res_gen_l1 = s.GEN_L1(p)(p=VSS, n=vdd)
            res_gen_m1 = s.GEN_M1(p)(p=VSS, n=vdd)
            res_gen_m2 = s.GEN_M2(p)(p=VSS, n=vdd)
            res_gen_m3 = s.GEN_M3(p)(p=VSS, n=vdd)
            res_gen_m4 = s.GEN_M4(p)(p=VSS, n=vdd)
            res_gen_m5 = s.GEN_M5(p)(p=VSS, n=vdd)

            res_gen_nd = s.GEN_ND(p)(p=VSS, n=vdd, b=VSS)
            res_gen_pd = s.GEN_PD(p)(p=VSS, n=vdd, b=VSS)
            res_gen_iso_pw = s.GEN_ISO_PW(p)(p=VSS, n=vdd, b=VSS)

        # Simulation Controls
        op = h.sim.Op()
        # wnf = h.sim.Options(wnflag=1)

        mc_mm_switch = h.sim.Param(0)
        mc_pr_switch = h.sim.Param(0)

        i1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt.spice"
        )
        i2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical.spice"
        )
        i3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical__lin.spice"
        )
        i4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/specialized_cells.spice"
        )
        # inc = sky130.install.include(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_precres():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = sky130.Sky130PrecResParams()

            res_p_prec_035 = s.PP_PREC_0p35(p)(p=VSS, n=vdd, b=VSS)
            res_p_prec_069 = s.PP_PREC_0p69(p)(p=VSS, n=vdd, b=VSS)
            res_p_prec_141 = s.PP_PREC_1p41(p)(p=VSS, n=vdd, b=VSS)
            res_p_prec_285 = s.PP_PREC_2p85(p)(p=VSS, n=vdd, b=VSS)
            res_p_prec_573 = s.PP_PREC_5p73(p)(p=VSS, n=vdd, b=VSS)
            res_p_minus_prec_035 = s.PM_PREC_0p35(p)(p=VSS, n=vdd, b=VSS)
            res_p_minus_prec_069 = s.PM_PREC_0p69(p)(p=VSS, n=vdd, b=VSS)
            res_p_minus_prec_141 = s.PM_PREC_1p41(p)(p=VSS, n=vdd, b=VSS)
            res_p_minus_prec_285 = s.PM_PREC_2p85(p)(p=VSS, n=vdd, b=VSS)
            res_p_minus_prec_573 = s.PM_PREC_5p73(p)(p=VSS, n=vdd, b=VSS)

        # Simulation Controls
        op = h.sim.Op()
        # wnf = h.sim.Options(wnflag=1)
        mc_mm_switch = h.sim.Param(0)
        mc_pr_switch = h.sim.Param(0)
        i1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt.spice"
        )
        i2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical.spice"
        )
        i3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical__lin.spice"
        )
        i4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/specialized_cells.spice"
        )
        # inc = sky130.install.include(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_bjt():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = sky130.Sky130BipolarParams()

            # FIXME: NPN Transistors currently require a hack
            npn_5_1x2 = s.NPN_5p0V_1x2(p)(c=VSS, b=vdd, e=VSS, s=VSS)
            # npn_11_1x1 = s.NPN_11p0V_1x1(p)(c=VSS,b=vdd,e=VSS,s=VSS) # This one just won't work...
            npn_5_1x1 = s.NPN_5p0V_1x1(p)(c=VSS, b=vdd, e=VSS, s=VSS)

            # These function without the hack below
            pnp_5_1x1 = s.PNP_5p0V_0p68x0p68(p)(c=VSS, b=vdd, e=VSS)
            pnp_5_3x3 = s.PNP_5p0V_3p40x3p40(p)(c=VSS, b=vdd, e=VSS)

        # Simulation Controls
        op = h.sim.Op()
        # wnf = h.sim.Options(wnflag=1)

        # Hack: https://open-source-silicon.slack.com/archives/C016UL7AQ73/p1680254109624109?thread_ts=1680112037.990359&cid=C016UL7AQ73
        dkisnpn1x1 = h.sim.Param(8.7913e-01)
        dkbfnpn1x1 = h.sim.Param(9.8501e-01)
        dkisnpn1x2 = h.sim.Param(9.0950e-01)
        dkbfnpn1x2 = h.sim.Param(9.6759e-01)
        dkisnpnpolyhv = h.sim.Param(1.0)
        dkbfnpnpolyhv = h.sim.Param(1.0)

        mc_mm_switch = h.sim.Param(0)
        mc_pr_switch = h.sim.Param(0)
        i1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt.spice"
        )
        i2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical.spice"
        )
        i3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical__lin.spice"
        )
        i4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/specialized_cells.spice"
        )

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_diode():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = sky130.Sky130DiodeParams()

            # FIXME: These are not working

            # All require a name starting with D

            pwnd_55v = s.PWND_5p5V(p)(p=vdd, n=VSS)
            pwnd_110v = s.PWND_11p0V(p)(p=vdd, n=VSS)
            nat_pwnd_55v = s.PWND_5p5V_NAT(p)(p=vdd, n=VSS)
            lvt_pwnd_55v = s.PWND_5p5V_LVT(p)(p=vdd, n=VSS)
            pdnw_55v = s.PDNW_5p5V(p)(p=vdd, n=VSS)
            pdnw_110v = s.PDNW_11p0V(p)(p=vdd, n=VSS)
            hvt_pdnw_55v = s.PDNW_5p5V_HVT(p)(p=vdd, n=VSS)
            lvt_pdnw_55v = s.PDNW_5p5V_LVT(p)(p=vdd, n=VSS)
            px_pwdn = s.PX_PWDN(p)(p=vdd, n=VSS)
            px_psdn = s.PX_PSDN(p)(p=vdd, n=VSS)
            px_psnw = s.PX_PSNW(p)(p=vdd, n=VSS)

            # RF diodes are just strange

            # px_rf_psnw = s.PX_RF_PSNW(p)(p=vdd, n=VSS)
            # px_rf_pwdn = s.PX_RF_PWDN(p)(p=vdd, n=VSS)

        # Simulation Controls
        op = h.sim.Op()
        # wnf = h.sim.Options(wnflag=1)
        mc_mm_switch = h.sim.Param(0)
        mc_pr_switch = h.sim.Param(0)
        i1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt.spice"
        )
        i2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical.spice"
        )
        i3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical__lin.spice"
        )
        i4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/specialized_cells.spice"
        )
        i5 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/rf.spice"
        )
        # inc = sky130.install.include(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_gencap():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = sky130.Sky130MimParams()
            q = sky130.Sky130VarParams()

            MIM_M3 = s.MIM_M3(p)(p=vdd, n=VSS)
            MIM_M4 = s.MIM_M4(p)(p=vdd, n=VSS)
            VAR_LVT = s.VAR_LVT(q)(p=vdd, n=VSS, b=VSS)
            VAR_HVT = s.VAR_HVT(q)(p=vdd, n=VSS, b=VSS)

        # Simulation Controls
        op = h.sim.Op()
        # wnf = h.sim.Options(wnflag=1)
        mc_mm_switch = h.sim.Param(0)
        mc_pr_switch = h.sim.Param(0)
        i1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt.spice"
        )
        i2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical.spice"
        )
        i3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical__lin.spice"
        )
        i4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/specialized_cells.spice"
        )
        # inc = sky130.install.include(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_devcap():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = sky130.Sky130VPPParams()

            # These work but you must include parameters from the
            # the first 5 which parameterize all the others

            cap_vpp_1 = s.VPP_PARA_1(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_2 = s.VPP_PARA_2(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_3 = s.VPP_PARA_3(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_4 = s.VPP_PARA_4(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_5 = s.VPP_PARA_5(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_6 = s.VPP_PARA_6(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_7 = s.VPP_PARA_7(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_8 = s.VPP_PARA_8(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_9 = s.VPP_PARA_9(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_10 = s.VPP_PARA_10(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_11 = s.VPP_PARA_11(p)(p=vdd, n=VSS, b=VSS)
            cap_vpp_12 = s.VPP_PERP_1(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_13 = s.VPP_PERP_2(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_14 = s.VPP_PERP_3(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_15 = s.VPP_PERP_4(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_16 = s.VPP_PERP_5(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_17 = s.VPP_PERP_6(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_18 = s.VPP_PERP_7(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_19 = s.VPP_PERP_8(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            cap_vpp_20 = s.VPP_PERP_9(p)(p=vdd, n=VSS, b=VSS, t=VSS)
            # cap_vpp_21 = s.VPP_PERP_10(p)(p=vdd, n=VSS, b=VSS, t=VSS)

        # Simulation Controls
        op = h.sim.Op()
        # wnf = h.sim.Options(wnflag=1)
        mc_mm_switch = h.sim.Param(0)
        mc_pr_switch = h.sim.Param(0)
        j1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.model_ref
            / "sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield_o2.spice"
        )

        j2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.model_ref
            / "sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield.spice"
        )

        j3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.model_ref
            / "sky130_fd_pr__cap_vpp_08p6x07p8_m1m2_noshield.spice"
        )

        j4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.model_ref
            / "sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield.spice"
        )

        j5 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.model_ref
            / "sky130_fd_pr__cap_vpp_11p5x11p7_m1m2_noshield.spice"
        )

        i1 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt.spice"
        )
        i2 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical.spice"
        )
        i3 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "r+c/res_typical__cap_typical__lin.spice"
        )
        i4 = h.sim.Include(
            sky130.install.pdk_path
            / sky130.install.lib_path.parent
            / "corners/tt/specialized_cells.spice"
        )
        # inc = sky130.install.include(h.pdk.Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)
