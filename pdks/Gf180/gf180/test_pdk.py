"""
# Global Foundries 180nm OSS PDK Plug-In 

Unit Tests
"""

from io import StringIO
import hdl21 as h
import gf180
from .pdk import modules as g
from hdl21.primitives import *


def mos_primitives_module():
    @h.module
    class MosPrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # Add all generic transistors
        nfet_03v3 = h.Nmos(h.MosParams(model="3.3V"))(d=z, g=z, s=z, b=z)
        pfet_03v3 = h.Pmos(h.MosParams(model="3.3V"))(d=z, g=z, s=z, b=z)
        nfet_06v0 = h.Nmos(h.MosParams(model="6.0V"))(d=z, g=z, s=z, b=z)
        pfet_06v0 = h.Pmos(h.MosParams(model="6.0V"))(d=z, g=z, s=z, b=z)
        nfet_03v3_dss = h.Nmos(h.MosParams(model="3.3V_DSS"))(d=z, g=z, s=z, b=z)
        pfet_03v3_dss = h.Pmos(h.MosParams(model="3.3V_DSS"))(d=z, g=z, s=z, b=z)
        nfet_06v0_dss = h.Nmos(h.MosParams(model="6.0V_DSS"))(d=z, g=z, s=z, b=z)
        pfet_06v0_dss = h.Pmos(h.MosParams(model="6.0V_DSS"))(d=z, g=z, s=z, b=z)
        nfet_06v0_nvt = h.Nmos(h.MosParams(model="NAT_6.0V"))(d=z, g=z, s=z, b=z)

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
        res_nd2ps_33v = h.Diode(model="ND2PS_3.3V")(p=z, n=z)
        res_pd2nw_33v = h.Diode(model="PD2NW_3.3V")(p=z, n=z)
        res_nd2ps_60v = h.Diode(model="ND2PS_6.0V")(p=z, n=z)
        res_pd2nw_60v = h.Diode(model="PD2NW_6.0V")(p=z, n=z)
        res_nw2ps_33v = h.Diode(model="NW2PS_3.3V")(p=z, n=z)
        res_nw2ps_60v = h.Diode(model="NW2PS_6.0V")(p=z, n=z)
        res_pw2dw = h.Diode(model="PW2DW")(p=z, n=z)
        res_dw2ps = h.Diode(model="DW2PS")(p=z, n=z)
        res_schottky = h.Diode(model="Schottky")(p=z, n=z)

    return DiodePrimitives


def bjt_primitives_module():
    @h.module
    class BjtPrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # Bipolar transistors
        pnp_10x042 = h.Pnp(model="10.0x0.42")
        pnp_5x042 = h.Pnp(model="5.0x0.42")
        pnp_10x100 = h.Pnp(model="10.0x10.0")
        pnp_5x50 = h.Pnp(model="5.0x5.0")
        npn_10x100 = h.FourTerminalBipolar(model="10.0x10.0", tp=BipolarType.NPN)
        npn_5x50 = h.FourTerminalBipolar(model="5.0x5.0", tp=BipolarType.NPN)
        npn_054x160 = h.FourTerminalBipolar(model="0.54x16.0", tp=BipolarType.NPN)
        npn_054x80 = h.FourTerminalBipolar(model="0.54x8.0", tp=BipolarType.NPN)
        npn_054x40 = h.FourTerminalBipolar(model="0.54x4.0", tp=BipolarType.NPN)
        npn_054x20 = h.FourTerminalBipolar(model="0.54x2.0", tp=BipolarType.NPN)

    return BjtPrimitives


def cap_primitives_module():
    @h.module
    class CapPrimitives:

        z = h.Signal(desc="Sole signal connected to everything")

        # Capacitors
        cap_15fF_MIM = h.PhysicalCapacitor(model="1.5fF_MIM")(p=z, n=z)
        cap_10fF_MIM = h.PhysicalCapacitor(model="1.0fF_MIM")(p=z, n=z)
        cap_20fF_MIM = h.PhysicalCapacitor(model="2.0fF_MIM")(p=z, n=z)

        # Three-terminal capacitors
        cap_33V_NMOS = h.ThreeTerminalCapacitor(model="3.3V_NMOS")(p=z, n=z, b=z)
        cap_33V_PMOS = h.ThreeTerminalCapacitor(model="3.3V_PMOS")(p=z, n=z, b=z)
        cap_60V_NMOS = h.ThreeTerminalCapacitor(model="6.0V_NMOS")(p=z, n=z, b=z)
        cap_60V_PMOS = h.ThreeTerminalCapacitor(model="6.0V_PMOS")(p=z, n=z, b=z)
        cap_33V_NMOS_Nwell = h.ThreeTerminalCapacitor(model="3.3V_NMOS_Nwell")(
            p=z, n=z, b=z
        )
        cap_33V_PMOS_Pwell = h.ThreeTerminalCapacitor(model="3.3V_PMOS_Pwell")(
            p=z, n=z, b=z
        )
        cap_60V_NMOS_Nwell = h.ThreeTerminalCapacitor(model="6.0V_NMOS_Nwell")(
            p=z, n=z, b=z
        )
        cap_60V_PMOS_Pwell = h.ThreeTerminalCapacitor(model="6.0V_PMOS_Pwell")(
            p=z, n=z, b=z
        )

    return CapPrimitives


def _compile_and_test(prims: h.Module, paramtype: h.Param):

    # Compile
    gf180.compile(prims)

    # ... and Test
    for k in prims.namespace:
        if k is not "z":

            assert isinstance(prims.namespace[k], h.Instance)
            assert isinstance(prims.namespace[k].of, h.ExternalModuleCall)
            assert isinstance(prims.namespace[k].of.params, paramtype)


def test_compile():

    _compile_and_test(mos_primitives_module(), gf180.GF180MosParams)
    _compile_and_test(res_primitives_module(), gf180.GF180ResParams)
    _compile_and_test(diode_primitives_module(), gf180.GF180DeviceParams)
    _compile_and_test(bjt_primitives_module(), gf180.GF180DeviceParams)
    _compile_and_test(cap_primitives_module(), gf180.GF180CapParams)


def _netlist(prims):

    # Netlist it for the PDK
    gf180.compile(prims)
    h.netlist(prims, StringIO(), fmt="spice")
    h.netlist(prims, StringIO(), fmt="spectre")
    h.netlist(prims, StringIO(), fmt="verilog")


def test_netlist():

    _netlist(mos_primitives_module())
    _netlist(res_primitives_module())
    _netlist(diode_primitives_module())
    _netlist(bjt_primitives_module())
    _netlist(cap_primitives_module())


def test_mos_module():

    p = gf180.GF180MosParams()

    @h.module
    class HasMos:

        nfet_03v3 = g.nfet_03v3(p)()
        pfet_03v3 = g.pfet_03v3(p)()
        nfet_06v0 = g.nfet_06v0(p)()
        pfet_06v0 = g.pfet_06v0(p)()
        nfet_03v3_dss = g.nfet_03v3_dss(p)()
        pfet_03v3_dss = g.pfet_03v3_dss(p)()
        nfet_06v0_dss = g.nfet_06v0_dss(p)()
        pfet_06v0_dss = g.pfet_06v0_dss(p)()
        nfet_06v0_nvt = g.nfet_06v0_nvt(p)()


def test_res_module():

    p = gf180.GF180ResParams()

    @h.module
    class HasRes:

        nplus_u = g.nplus_u(p)()
        pplus_u = g.pplus_u(p)()
        nplus_s = g.nplus_s(p)()
        pplus_s = g.pplus_s(p)()
        nwell = g.nwell(p)()
        npolyf_u = g.npolyf_u(p)()
        ppolyf_u = g.ppolyf_u(p)()
        npolyf_s = g.npolyf_s(p)()
        ppolyf_s = g.ppolyf_s(p)()
        ppolyf_u_1k = g.ppolyf_u_1k(p)()
        ppolyf_u_2k = g.ppolyf_u_2k(p)()
        ppolyf_u_1k_6p0 = g.ppolyf_u_1k_6p0(p)()
        ppolyf_u_2k_6p0 = g.ppolyf_u_2k_6p0(p)()
        ppolyf_u_3k = g.ppolyf_u_3k(p)()
        rm1 = g.rm1(p)()
        rm2 = g.rm2(p)()
        rm3 = g.rm3(p)()
        tm6k = g.tm6k(p)()
        tm9k = g.tm9k(p)()
        tm11k = g.tm11k(p)()
        tm30k = g.tm30k(p)()


def test_cap_module():

    p = gf180.GF180CapParams()

    @h.module
    class HasCap:

        cap_mim_1f5fF = g.cap_mim_1f5fF(p)()
        cap_mim_1f0fF = g.cap_mim_1f0fF(p)()
        cap_mim_2f0fF = g.cap_mim_2f0fF(p)()
        cap_nmos_03v3 = g.cap_nmos_03v3(p)()
        cap_pmos_03v3 = g.cap_pmos_03v3(p)()
        cap_nmos_06v0 = g.cap_nmos_06v0(p)()
        cap_pmos_06v0 = g.cap_pmos_06v0(p)()
        cap_nmos_03v3_b = g.cap_nmos_03v3_b(p)()
        cap_pmos_03v3_b = g.cap_pmos_03v3_b(p)()
        cap_nmos_06v0_b = g.cap_nmos_06v0_b(p)()
        cap_pmos_06v0_b = g.cap_pmos_06v0_b(p)()


def test_diodes_module():

    p = gf180.GF180DeviceParams()

    @h.module
    class HasDiode:

        diode_nd2ps_03v3 = g.diode_nd2ps_03v3(p)()
        diode_pd2nw_03v3 = g.diode_pd2nw_03v3(p)()
        diode_nd2ps_06v0 = g.diode_nd2ps_06v0(p)()
        diode_pd2nw_06v0 = g.diode_pd2nw_06v0(p)()
        diode_nw2ps_03v3 = g.diode_nw2ps_03v3(p)()
        diode_nw2ps_06v0 = g.diode_nw2ps_06v0(p)()
        diode_pw2dw = g.diode_pw2dw(p)()
        diode_dw2ps = g.diode_dw2ps(p)()
        sc_diode = g.sc_diode(p)()


def test_bjt_module():

    p = gf180.GF180DeviceParams()

    @h.module
    class HasBJT:

        pnp_10p00x00p42 = g.pnp_10p00x00p42(p)()
        pnp_05p00x00p42 = g.pnp_05p00x00p42(p)()
        pnp_10p00x10p00 = g.pnp_10p00x10p00(p)()
        pnp_05p00x05p00 = g.pnp_05p00x05p00(p)()
        npn_10p00x10p00 = g.npn_10p00x10p00(p)()
        npn_05p00x05p00 = g.npn_05p00x05p00(p)()
        npn_00p54x16p00 = g.npn_00p54x16p00(p)()
        npn_00p54x08p00 = g.npn_00p54x08p00(p)()
        npn_00p54x04p00 = g.npn_00p54x04p00(p)()
        npn_00p54x02p00 = g.npn_00p54x02p00(p)()

def test_walker_contents():
    from hdl21.tests.content import walker_test_content

    content = walker_test_content()
    gf180.compile(content)
