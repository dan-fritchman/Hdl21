"""
# Global Foundries 180nm OSS PDK Plug-In 

Unit Tests
"""

from io import StringIO
import hdl21 as h
import gf180_hdl21
import gf180_hdl21.primitives as g
from hdl21.primitives import *


def mos_primitives_module():
    @h.module
    class MosPrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # Add all generic transistors
        nfet_03v3 = h.Mos(model="PFET_3p3V")(d=z, g=z, s=z, b=z)
        pfet_03v3 = h.Mos(model="NFET_3p3V")(d=z, g=z, s=z, b=z)
        nfet_06v0 = h.Mos(model="NFET_6p0V")(d=z, g=z, s=z, b=z)
        pfet_06v0 = h.Mos(model="PFET_6p0V")(d=z, g=z, s=z, b=z)
        nfet_03v3_dss = h.Mos(model="NFET_3p3V_DSS")(d=z, g=z, s=z, b=z)
        pfet_03v3_dss = h.Mos(model="PFET_3p3V_DSS")(d=z, g=z, s=z, b=z)
        nfet_06v0_dss = h.Mos(model="NFET_6p0V_DSS")(d=z, g=z, s=z, b=z)
        pfet_06v0_dss = h.Mos(model="PFET_6p0V_DSS")(d=z, g=z, s=z, b=z)
        nfet_06v0_nvt = h.Mos(model="NFET_6p0V_NAT")(d=z, g=z, s=z, b=z)

    return MosPrimitives


def res_primitives_module():
    @h.module
    class ResPrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # 3-terminal resistors
        res_nplus_u = h.ThreeTerminalResistor(model="NPLUS_U")(p=z, n=z, b=z)
        res_pplus_u = h.ThreeTerminalResistor(model="PPLUS_U")(p=z, n=z, b=z)
        res_nplus_s = h.ThreeTerminalResistor(model="NPLUS_S")(p=z, n=z, b=z)
        res_pplus_s = h.ThreeTerminalResistor(model="PPLUS_S")(p=z, n=z, b=z)
        res_nwell = h.ThreeTerminalResistor(model="NWELL")(p=z, n=z, b=z)
        res_npolyf_u = h.ThreeTerminalResistor(model="NPOLYF_U")(p=z, n=z, b=z)
        res_ppolyf_u = h.ThreeTerminalResistor(model="PPOLYF_U")(p=z, n=z, b=z)
        res_npolyf_s = h.ThreeTerminalResistor(model="NPOLYF_S")(p=z, n=z, b=z)
        res_ppolyf_s = h.ThreeTerminalResistor(model="PPOLYF_S")(p=z, n=z, b=z)
        res_ppolyf_u_1k = h.ThreeTerminalResistor(model="PPOLYF_U_1K")(p=z, n=z, b=z)
        res_ppolyf_u_2k = h.ThreeTerminalResistor(model="PPOLYF_U_2K")(p=z, n=z, b=z)
        res_ppolyf_u_1k_6p0 = h.ThreeTerminalResistor(model="PPOLYF_U_1K_6P0")(
            p=z, n=z, b=z
        )
        res_ppolyf_u_2k_6p0 = h.ThreeTerminalResistor(model="PPOLYF_U_2K_6P0")(
            p=z, n=z, b=z
        )
        res_ppolyf_u_3k = h.ThreeTerminalResistor(model="PPOLYF_U_3K")(p=z, n=z, b=z)

        # 2-terminal resistors
        res_rm1 = h.PhysicalResistor(model="RM1")(p=z, n=z)
        res_rm2 = h.PhysicalResistor(model="RM2")(p=z, n=z)
        res_rm3 = h.PhysicalResistor(model="RM3")(p=z, n=z)
        res_tm6k = h.PhysicalResistor(model="TM6K")(p=z, n=z)
        res_tm9k = h.PhysicalResistor(model="TM9K")(p=z, n=z)
        res_tm11k = h.PhysicalResistor(model="TM11K")(p=z, n=z)
        res_tm30k = h.PhysicalResistor(model="TM30K")(p=z, n=z)

    return ResPrimitives


def diode_primitives_module():
    @h.module
    class DiodePrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # Diodes
        diode_nd2ps_33v = h.Diode(model="ND2PS_3p3V")(p=z, n=z)
        diode_pd2nw_33v = h.Diode(model="PD2NW_3p3V")(p=z, n=z)
        diode_nd2ps_60v = h.Diode(model="ND2PS_6p0V")(p=z, n=z)
        diode_pd2nw_60v = h.Diode(model="PD2NW_6p0V")(p=z, n=z)
        diode_nw2ps_33v = h.Diode(model="NW2PS_3p3V")(p=z, n=z)
        diode_nw2ps_60v = h.Diode(model="NW2PS_6p0V")(p=z, n=z)
        diode_pw2dw = h.Diode(model="PW2DW")(p=z, n=z)
        diode_dw2ps = h.Diode(model="DW2PS")(p=z, n=z)
        diode_schottky = h.Diode(model="Schottky")(p=z, n=z)

    return DiodePrimitives


def bjt_primitives_module():
    @h.module
    class BjtPrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # Bipolar transistors
        pnp_10x042 = h.Pnp(model="PNP_10p0x0p42")
        pnp_5x042 = h.Pnp(model="PNP_5p0x0p42")
        pnp_10x100 = h.Pnp(model="PNP_10p0x10p0")
        pnp_5x50 = h.Pnp(model="PNP_5p0x5p0")

    return BjtPrimitives


def cap_primitives_module():
    @h.module
    class CapPrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # Capacitors
        cap_15fF_MIM = h.PhysicalCapacitor(model="MIM_1p5fF")(p=z, n=z)
        cap_10fF_MIM = h.PhysicalCapacitor(model="MIM_1p0fF")(p=z, n=z)
        cap_20fF_MIM = h.PhysicalCapacitor(model="MIM_2p0fF")(p=z, n=z)

        # Three-terminal capacitors
        cap_33V_NMOS = h.ThreeTerminalCapacitor(model="NMOS_3p3V")(p=z, n=z, b=z)
        cap_33V_PMOS = h.ThreeTerminalCapacitor(model="PMOS_3p3V")(p=z, n=z, b=z)
        cap_60V_NMOS = h.ThreeTerminalCapacitor(model="NMOS_6p0V")(p=z, n=z, b=z)
        cap_60V_PMOS = h.ThreeTerminalCapacitor(model="PMOS_6p0V")(p=z, n=z, b=z)
        cap_33V_NMOS_Nwell = h.ThreeTerminalCapacitor(model="NMOS_Nwell_3p3V")(
            p=z, n=z, b=z
        )
        cap_33V_PMOS_Pwell = h.ThreeTerminalCapacitor(model="PMOS_Pwell_3p3V")(
            p=z, n=z, b=z
        )
        cap_60V_NMOS_Nwell = h.ThreeTerminalCapacitor(model="NMOS_Nwell_6p0V")(
            p=z, n=z, b=z
        )
        cap_60V_PMOS_Pwell = h.ThreeTerminalCapacitor(model="PMOS_Pwell_6p0V")(
            p=z, n=z, b=z
        )

    return CapPrimitives


def _compile_and_test(prims: h.Module, paramtype: h.Param):

    # Compile
    gf180_hdl21.compile(prims)

    # ... and Test
    for k in prims.namespace:
        if k is not "z":

            assert isinstance(prims.namespace[k], h.Instance)
            assert isinstance(prims.namespace[k].of, h.ExternalModuleCall)
            assert isinstance(prims.namespace[k].of.params, paramtype)


def test_compile():

    _compile_and_test(mos_primitives_module(), gf180_hdl21.GF180MosParams)
    _compile_and_test(res_primitives_module(), gf180_hdl21.GF180ResParams)
    _compile_and_test(diode_primitives_module(), gf180_hdl21.GF180DiodeParams)
    _compile_and_test(bjt_primitives_module(), gf180_hdl21.GF180BipolarParams)
    _compile_and_test(cap_primitives_module(), gf180_hdl21.GF180CapParams)


def _netlist(prims):

    # Netlist it for the PDK
    gf180_hdl21.compile(prims)
    h.netlist(prims, StringIO(), fmt="spice")
    h.netlist(prims, StringIO(), fmt="spectre")


def test_netlist():

    _netlist(mos_primitives_module())
    _netlist(res_primitives_module())
    _netlist(diode_primitives_module())
    _netlist(bjt_primitives_module())
    _netlist(cap_primitives_module())


def test_mos_module():

    p = gf180_hdl21.GF180MosParams()

    @h.module
    class HasMos:

        nfet_03v3 = g.PFET_3p3V(p)()
        pfet_03v3 = g.NFET_3p3V(p)()
        nfet_06v0 = g.NFET_6p0V(p)()
        pfet_06v0 = g.PFET_6p0V(p)()
        nfet_03v3_dss = g.NFET_3p3V_DSS(p)()
        pfet_03v3_dss = g.PFET_3p3V_DSS(p)()
        nfet_06v0_dss = g.NFET_6p0V_DSS(p)()
        pfet_06v0_dss = g.PFET_6p0V_DSS(p)()
        nfet_06v0_nvt = g.NFET_6p0V_NAT(p)()


def test_res_module():

    p = gf180_hdl21.GF180ResParams()

    @h.module
    class HasRes:

        nplus_u = g.NPLUS_U(p)()
        pplus_u = g.PPLUS_U(p)()
        nplus_s = g.NPLUS_S(p)()
        pplus_s = g.PPLUS_S(p)()
        nwell = g.NWELL(p)()
        npolyf_u = g.NPOLYF_U(p)()
        ppolyf_u = g.PPOLYF_U(p)()
        npolyf_s = g.NPOLYF_S(p)()
        ppolyf_s = g.PPOLYF_S(p)()
        ppolyf_u_1k = g.PPOLYF_U_1K(p)()
        ppolyf_u_2k = g.PPOLYF_U_2K(p)()
        ppolyf_u_1k_6p0 = g.PPOLYF_U_1K_6P0(p)()
        ppolyf_u_2k_6p0 = g.PPOLYF_U_2K_6P0(p)()
        ppolyf_u_3k = g.PPOLYF_U_3K(p)()
        rm1 = g.RM1(p)()
        rm2 = g.RM2(p)()
        rm3 = g.RM3(p)()
        tm6k = g.TM6K(p)()
        tm9k = g.TM9K(p)()
        tm11k = g.TM11K(p)()
        tm30k = g.TM30K(p)()


def test_cap_module():

    p = gf180_hdl21.GF180CapParams()

    @h.module
    class HasCap:

        cap_mim_1f5fF = g.MIM_1p5fF(p)()
        cap_mim_1f0fF = g.MIM_1p0fF(p)()
        cap_mim_2f0fF = g.MIM_2p0fF(p)()
        cap_nmos_03v3 = g.NMOS_3p3V(p)()
        cap_pmos_03v3 = g.PMOS_3p3V(p)()
        cap_nmos_06v0 = g.NMOS_6p0V(p)()
        cap_pmos_06v0 = g.PMOS_6p0V(p)()
        cap_nmos_03v3_b = g.NMOS_Nwell_3p3V(p)()
        cap_pmos_03v3_b = g.PMOS_Pwell_3p3V(p)()
        cap_nmos_06v0_b = g.NMOS_Nwell_6p0V(p)()
        cap_pmos_06v0_b = g.PMOS_Pwell_6p0V(p)()


def test_diodes_module():

    p = gf180_hdl21.GF180DiodeParams()

    @h.module
    class HasDiode:

        diode_nd2ps_03v3 = g.ND2PS_3p3V(p)()
        diode_pd2nw_03v3 = g.PD2NW_3p3V(p)()
        diode_nd2ps_06v0 = g.ND2PS_6p0V(p)()
        diode_pd2nw_06v0 = g.PD2NW_6p0V(p)()
        diode_nw2ps_03v3 = g.NW2PS_3p3V(p)()
        diode_nw2ps_06v0 = g.NW2PS_6p0V(p)()
        diode_pw2dw = g.PW2DW(p)()
        diode_dw2ps = g.DW2PS(p)()
        sc_diode = g.Schottky(p)()


def test_bjt_module():

    p = gf180_hdl21.GF180BipolarParams()

    @h.module
    class HasBJT:

        pnp_10p00x00p42 = g.PNP_10p0x0p42(p)()
        pnp_05p00x00p42 = g.PNP_5p0x0p42(p)()
        pnp_10p00x10p00 = g.PNP_10p0x10p0(p)()
        pnp_05p00x05p00 = g.PNP_5p0x5p0(p)()
        npn_10p00x10p00 = g.NPN_10p0x10p0(p)()
        npn_05p00x05p00 = g.NPN_5p0x5p0(p)()
        npn_00p54x16p00 = g.NPN_0p54x16p0(p)()
        npn_00p54x08p00 = g.NPN_0p54x8p0(p)()
        npn_00p54x04p00 = g.NPN_0p54x4p0(p)()
        npn_00p54x02p00 = g.NPN_0p54x2p0(p)()


def test_walker_contents():
    from hdl21.tests.content import walker_test_content

    content = walker_test_content()
    gf180_hdl21.compile(content)
