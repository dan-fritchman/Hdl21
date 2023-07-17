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
import gf180_hdl21
import hdl21 as h
from hdl21.prefix import µ
from hdl21.pdk import Corner, CmosCorner
import vlsirtools.spice as vsp
import gf180_hdl21.primitives as g


def test_installed():
    """
        Test if the PDK is installed and properly configured.

        This test checks if the PDK `gf180.install` is not None and if its type
        is `gf180.Install`. If both conditio
    ns are met, the test passes.
    """
    assert gf180_hdl21.install is not None
    assert isinstance(gf180_hdl21.install, gf180_hdl21.Install)


def test_sim_mosfets():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = gf180_hdl21.GF180MosParams

            nfet_03v3 = g.NFET_3p3V(p(w=0.220 * µ, l=0.280 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            pfet_03v3 = g.PFET_3p3V(p(w=0.220 * µ, l=0.280 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            nfet_06v0 = g.NFET_6p0V(p(w=0.300 * µ, l=0.700 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            pfet_06v0 = g.PFET_6p0V(p(w=0.300 * µ, l=0.500 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )

            nfet_03v3_dss = g.NFET_3p3V_DSS(p(w=0.220 * µ, l=0.280 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            pfet_03v3_dss = g.PFET_3p3V_DSS(p(w=0.220 * µ, l=0.280 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )
            # nfet_06v0_dss = g.NFET_6p0V_DSS(p(w = 0.300 * µ,l = 0.500 * µ))(d=vdd, g=vdd, s=VSS, b=VSS)
            pfet_06v0_dss = g.PFET_6p0V_DSS(p(w=0.300 * µ, l=0.500 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )

            nfet_06v0_nvt = g.NFET_6p0V_NAT(p(w=0.800 * µ, l=1.800 * µ))(
                d=vdd, g=vdd, s=VSS, b=VSS
            )

        # Simulation Controls
        op = h.sim.Op()
        i1 = gf180_hdl21.install.include_design()
        i2 = gf180_hdl21.install.include_mos(CmosCorner.TT)

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
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = gf180_hdl21.GF180ResParams()

            # Three terminal resistors
            nplus_u = g.NPLUS_U(p)(p=vdd, n=VSS, b=VSS)
            pplus_u = g.PPLUS_U(p)(p=vdd, n=VSS, b=VSS)
            nplus_s = g.NPLUS_S(p)(p=vdd, n=VSS, b=VSS)
            pplus_s = g.PPLUS_S(p)(p=vdd, n=VSS, b=VSS)
            nwell = g.NWELL(p)(p=vdd, n=VSS, b=VSS)
            npolyf_u = g.NPOLYF_U(p)(p=vdd, n=VSS, b=VSS)
            ppolyf_u = g.PPOLYF_U(p)(p=vdd, n=VSS, b=VSS)
            npolyf_s = g.NPOLYF_S(p)(p=vdd, n=VSS, b=VSS)
            ppolyf_s = g.PPOLYF_S(p)(p=vdd, n=VSS, b=VSS)
            ppolyf_u_1k = g.PPOLYF_U_1K(p)(p=vdd, n=VSS, b=VSS)
            ppolyf_u_2k = g.PPOLYF_U_2K(p)(p=vdd, n=VSS, b=VSS)
            ppolyf_u_1k_6p0 = g.PPOLYF_U_1K_6P0(p)(p=vdd, n=VSS, b=VSS)
            ppolyf_u_2k_6p0 = g.PPOLYF_U_2K_6P0(p)(p=vdd, n=VSS, b=VSS)
            ppolyf_u_3k = g.PPOLYF_U_3K(p)(p=vdd, n=VSS, b=VSS)

            # Two terminal resistors
            rm1 = g.RM1(p)(p=vdd, n=VSS)
            rm2 = g.RM2(p)(p=vdd, n=VSS)
            rm3 = g.RM3(p)(p=vdd, n=VSS)
            tm6k = g.TM6K(p)(p=vdd, n=VSS)
            tm9k = g.TM9K(p)(p=vdd, n=VSS)
            tm11k = g.TM11K(p)(p=vdd, n=VSS)
            tm30k = g.TM30K(p)(p=vdd, n=VSS)

        # Simulation Controls
        op = h.sim.Op()

        d1 = gf180_hdl21.install.include_design()
        i1 = gf180_hdl21.install.include_mos(CmosCorner.TT)
        i2 = gf180_hdl21.install.include_resistors(Corner.TYP)

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
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = gf180_hdl21.GF180CapParams

            cap_mim_1f5fF = g.MIM_1p5fF(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_mim_1f0fF = g.MIM_1p0fF(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_mim_2f0fF = g.MIM_2p0fF(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )

            cap_nmos_03v3 = g.NMOS_3p3V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_pmos_03v3 = g.PMOS_3p3V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_nmos_06v0 = g.NMOS_6p0V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_pmos_06v0 = g.PMOS_6p0V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_nmos_03v3_b = g.NMOS_Nwell_3p3V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_pmos_03v3_b = g.PMOS_Pwell_3p3V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_nmos_06v0_b = g.NMOS_Nwell_6p0V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )
            cap_pmos_06v0_b = g.PMOS_Pwell_6p0V(p(c_width=10 * μ, c_length=10 * μ))(
                p=vdd, n=VSS
            )

        # Simulation Controls
        op = h.sim.Op()

        d1 = gf180_hdl21.install.include_design()
        i1 = gf180_hdl21.install.include_mos(CmosCorner.TT)
        #! Very important that this is included!
        i11 = h.sim.Lib(gf180_hdl21.install.model_lib, "cap_mim")
        i2 = gf180_hdl21.install.include_resistors(Corner.TYP)
        i3 = gf180_hdl21.install.include_moscaps(Corner.TYP)
        i4 = gf180_hdl21.install.include_mimcaps(Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)


def test_sim_diodes():
    @h.sim.sim
    class Sim:
        @h.module
        class Tb:

            VSS = h.Port()
            vdd = h.Signal()
            v = h.Vdc(dc=1)(p=vdd, n=VSS)

            p = gf180_hdl21.GF180DiodeParams()

            diode_nd2ps_03v3 = g.ND2PS_3p3V(p)(p=vdd, n=VSS)
            diode_pd2nw_03v3 = g.PD2NW_3p3V(p)(p=vdd, n=VSS)
            diode_nd2ps_06v0 = g.ND2PS_6p0V(p)(p=vdd, n=VSS)
            diode_pd2nw_06v0 = g.PD2NW_6p0V(p)(p=vdd, n=VSS)
            diode_nw2ps_03v3 = g.NW2PS_3p3V(p)(p=vdd, n=VSS)
            diode_nw2ps_06v0 = g.NW2PS_6p0V(p)(p=vdd, n=VSS)
            diode_pw2dw = g.PW2DW(p)(p=vdd, n=VSS)
            diode_dw2ps = g.DW2PS(p)(p=vdd, n=VSS)
            sc_diode = g.Schottky(p)(p=vdd, n=VSS)

        # Simulation Controls
        op = h.sim.Op()

        i1 = gf180_hdl21.install.include_diodes(Corner.TYP)

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

            p = gf180_hdl21.GF180BipolarParams()

            pnp_10p00x00p42 = g.PNP_10p0x0p42(p)(c=vdd, b=VSS, e=vdd)
            pnp_05p00x00p42 = g.PNP_5p0x0p42(p)(c=vdd, b=VSS, e=vdd)
            pnp_10p00x10p00 = g.PNP_10p0x10p0(p)(c=vdd, b=VSS, e=vdd)
            pnp_05p00x05p00 = g.PNP_5p0x5p0(p)(c=vdd, b=VSS, e=vdd)
            npn_10p00x10p00 = g.NPN_10p0x10p0(p)(c=vdd, b=VSS, e=vdd, s=VSS)
            npn_05p00x05p00 = g.NPN_5p0x5p0(p)(c=vdd, b=VSS, e=vdd, s=VSS)
            npn_00p54x16p00 = g.NPN_0p54x16p0(p)(c=vdd, b=VSS, e=vdd, s=VSS)
            npn_00p54x08p00 = g.NPN_0p54x8p0(p)(c=vdd, b=VSS, e=vdd, s=VSS)
            npn_00p54x04p00 = g.NPN_0p54x4p0(p)(c=vdd, b=VSS, e=vdd, s=VSS)
            npn_00p54x02p00 = g.NPN_0p54x2p0(p)(c=vdd, b=VSS, e=vdd, s=VSS)

        # Simulation Controls
        op = h.sim.Op()

        d1 = gf180_hdl21.install.include_design()
        i1 = gf180_hdl21.install.include_mos(CmosCorner.TT)
        i2 = gf180_hdl21.install.include_resistors(Corner.TYP)
        i3 = gf180_hdl21.install.include_moscaps(Corner.TYP)
        i4 = gf180_hdl21.install.include_bjts(Corner.TYP)

    opts = vsp.SimOptions(
        simulator=vsp.SupportedSimulators.NGSPICE,
        fmt=vsp.ResultFormat.SIM_DATA,
        rundir="./scratch",
    )

    rv = Sim.run(opts)
    assert isinstance(rv, vsp.sim_data.SimResult)

    op = rv[vsp.sim_data.AnalysisType.OP]
    assert isinstance(op, vsp.sim_data.OpResult)
