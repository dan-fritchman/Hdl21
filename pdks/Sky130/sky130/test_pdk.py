"""
# SkyWater 130nm OSS PDK Plug-In 

Unit Tests
"""

from io import StringIO
import hdl21 as h
from . import pdk as sky130
from .pdk import modules as s
from hdl21.prefix import µ
from hdl21.primitives import *


def test_default():
    h.pdk.set_default(sky130)
    assert h.pdk.default() is sky130


def mos_primitives_module():
    @h.module
    class Primitives:
        """Module with all the primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        # Add all generic transistors
        nfet_01v8 = h.Nmos(h.MosParams(model="1.8V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_01v8 = h.Nmos(h.MosParams(model="1.8V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_01v8_lvt = h.Pmos(h.MosParams(model="1.8V", vth=MosVth.LOW))(
            d=z, g=z, s=z, b=z
        )
        pfet_01v8 = h.Pmos(h.MosParams(model="1.8V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        pfet_01v8_hvt = h.Pmos(h.MosParams(model="1.8V", vth=MosVth.HIGH))(
            d=z, g=z, s=z, b=z
        )
        pfet_01v8_lvt = h.Pmos(h.MosParams(model="1.8V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        pfet_g5v0d10v5 = h.Pmos(h.MosParams(model="5.5V_D10", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_g5v0d10v5 = h.Nmos(h.MosParams(model="5.5V_D10", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        pfet_g5v0d16v0 = h.Pmos(h.MosParams(model="5.5V_D16", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_20v0 = h.Nmos(h.MosParams(model="20.0V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_20v0_zvt = h.Nmos(h.MosParams(model="20.0V", vth=MosVth.ULTRA_LOW))(
            d=z, g=z, s=z, b=z
        )

        # Add Native FET Transistors
        nfet_20v0_iso = h.Nmos(h.MosParams(model="ISO_20.0V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        pfet_20v0 = h.Pmos(h.MosParams(model="20.0V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_03v3_nvt = h.Nmos(h.MosParams(model="NAT_3.3V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_05v0_nvt = h.Nmos(h.MosParams(model="NAT_5.0V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        nfet_20v0_nvt = h.Nmos(h.MosParams(model="NAT_20.0V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        esd_nfet_01v8 = h.Nmos(h.MosParams(model="ESD_1.8V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        esd_nfet_g5v0d10v5 = h.Nmos(h.MosParams(model="ESD_5.5V_D10", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        esd_nfet_g5v0d10v5_nvt = h.Nmos(h.MosParams(model="ESD_5.5V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )
        esd_pfet_g5v0d10v5 = h.Pmos(h.MosParams(model="NAT_ESD_5.5V", vth=MosVth.STD))(
            d=z, g=z, s=z, b=z
        )

    return Primitives


def genres_primitives_module():
    @h.module
    class ResistorPrimitives:
        """Module with all the generic resistor primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        res_gen_po = h.PhysicalResistor(model="GEN_PO")(p=z, n=z)
        res_gen_li = h.PhysicalResistor(model="GEN_LI")(p=z, n=z)
        res_gen_m1 = h.PhysicalResistor(model="GEN_M1")(p=z, n=z)
        res_gen_m2 = h.PhysicalResistor(model="GEN_M2")(p=z, n=z)
        res_gen_m3 = h.PhysicalResistor(model="GEN_M3")(p=z, n=z)
        res_gen_m4 = h.PhysicalResistor(model="GEN_M4")(p=z, n=z)
        res_gen_m5 = h.PhysicalResistor(model="GEN_M5")(p=z, n=z)

        res_gen_nd = h.ThreeTerminalResistor(model="GEN_ND")(p=z, n=z, b=z)
        res_gen_pd = h.ThreeTerminalResistor(model="GEN_PD")(p=z, n=z, b=z)
        res_gen_iso_pw = h.ThreeTerminalResistor(model="GEN_ISO_PW")(p=z, n=z, b=z)

    return ResistorPrimitives


def precres_primitives_module():
    @h.module
    class ResistorPrimitives:
        """Module with all the precision resistor primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        res_p_prec_035 = h.ThreeTerminalResistor(model="P+_PREC_0.35")(p=z, n=z, b=z)
        res_p_prec_069 = h.ThreeTerminalResistor(model="P+_PREC_0.69")(p=z, n=z, b=z)
        res_p_prec_141 = h.ThreeTerminalResistor(model="P+_PREC_1.41")(p=z, n=z, b=z)
        res_p_prec_285 = h.ThreeTerminalResistor(model="P+_PREC_2.85")(p=z, n=z, b=z)
        res_p_prec_530 = h.ThreeTerminalResistor(model="P+_PREC_5.30")(p=z, n=z, b=z)

        res_p_minus_prec_035 = h.ThreeTerminalResistor(model="P-_PREC_0.35")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_069 = h.ThreeTerminalResistor(model="P-_PREC_0.69")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_141 = h.ThreeTerminalResistor(model="P-_PREC_1.41")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_285 = h.ThreeTerminalResistor(model="P-_PREC_2.85")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_530 = h.ThreeTerminalResistor(model="P-_PREC_5.30")(
            p=z, n=z, b=z
        )

    return ResistorPrimitives


def diode_primitives_module():
    @h.module
    class DiodePrimitives:
        """Module with all the diode primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        pwnd_55v = h.Diode(model="PWND_5.5V")(p=z, n=z)
        pwnd_110v = h.Diode(model="PWND_11.0V")(p=z, n=z)
        nat_pwnd_55v = h.Diode(model="NAT_PWND_5.5V")(p=z, n=z)
        lvt_pwnd_55v = h.Diode(model="LVT_PWND_5.5V")(p=z, n=z)
        pdnw_55v = h.Diode(model="PDNW_5.5V")(p=z, n=z)
        pdnw_110v = h.Diode(model="PDNW_11.0V")(p=z, n=z)
        hvt_pdnw_55v = h.Diode(model="HVT_PDNW_5.5V")(p=z, n=z)
        lvt_pdnw_55v = h.Diode(model="LVT_PDNW_5.5V")(p=z, n=z)
        px_rf_psnw = h.Diode(model="PX_RF_PSNW")(p=z, n=z)
        px_rf_pwdn = h.Diode(model="PX_RF_PWDN")(p=z, n=z)
        px_pwdn = h.Diode(model="PX_PWDN")(p=z, n=z)
        px_psdn = h.Diode(model="PX_PSDN")(p=z, n=z)
        px_psnw = h.Diode(model="PX_PSNW")(p=z, n=z)

    return DiodePrimitives


def bjt_primitives_module():
    @h.module
    class BjtPrimitives:
        """Module with all the Bipolar transistor primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        npn_50v = h.Npn(model="5.0V")
        npn_110v = h.Npn(model="11.0V")
        pnp_50v = h.Pnp(model="5.0V")

    return BjtPrimitives


def mimcap_primitives_module():
    @h.module
    class CapacitorPrimitives:
        """Module with all the generic capacitor primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        MIM_M3 = h.PhysicalCapacitor(model="MIM_M3")(p=z, n=z)
        MIM_M4 = h.PhysicalCapacitor(model="MIM_M4")(p=z, n=z)

    return CapacitorPrimitives

def varcap_primitives_module():
        
    @h.module
    class CapacitorPrimitives:
    
        z = h.Signal(desc="Sole signal connected to everything")

        VAR_LVT = h.ThreeTerminalCapacitor(model="VAR_LVT")(p=z, n=z, b=z)
        VAR_HVT = h.ThreeTerminalCapacitor(model="VAR_HVT")(p=z, n=z, b=z)

    return CapacitorPrimitives

def vppcap_primitives_module():
    @h.module
    class CapacitorPrimitives:
        """Module with all the device capacitor primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        # Parallel VPP capacitors
        cap_vpp_1 = h.ThreeTerminalCapacitor(
            model="VPP_PARA_1"
        )(p=z, n=z, b=z)
        cap_vpp_2 = h.ThreeTerminalCapacitor(model="VPP_PARA_2")(
            p=z, n=z, b=z
        )
        cap_vpp_3 = h.ThreeTerminalCapacitor(model="VPP_PARA_3")(
            p=z, n=z, b=z
        )
        cap_vpp_4 = h.ThreeTerminalCapacitor(model="VPP_PARA_4")(
            p=z, n=z, b=z
        )
        cap_vpp_5 = h.ThreeTerminalCapacitor(model="VPP_PARA_5")(
            p=z, n=z, b=z
        )
        cap_vpp_6 = h.ThreeTerminalCapacitor(
            model="VPP_PARA_6"
        )(p=z, n=z, b=z)
        cap_vpp_7 = h.ThreeTerminalCapacitor(
            model="VPP_PARA_7"
        )(p=z, n=z, b=z)
        cap_vpp_8 = h.ThreeTerminalCapacitor(
            model="VPP_PARA_8"
        )(p=z, n=z, b=z)
        cap_vpp_9 = h.ThreeTerminalCapacitor(
            model="VPP_PARA_9"
        )(p=z, n=z, b=z)
        cap_vpp_10 = h.ThreeTerminalCapacitor(
            model="VPP_PARA_10"
        )(p=z, n=z, b=z)
        cap_vpp_11 = h.ThreeTerminalCapacitor(
            model="VPP_PARA_11"
        )(p=z, n=z, b=z)

        # Perpendicular VPP capacitors
        cap_vpp_12 = h.ShieldedCapacitor(model="VPP_PERP_1")(
            p=z, n=z, s=z, t=z
        )
        cap_vpp_13 = h.ShieldedCapacitor(
            model="VPP_PERP_2"
        )(p=z, n=z, s=z, t=z)
        cap_vpp_14 = h.ShieldedCapacitor(model="VPP_PERP_3")(
            p=z, n=z, s=z, t=z
        )
        cap_vpp_15 = h.ShieldedCapacitor(
            model="VPP_PERP_4"
        )(p=z, n=z, s=z, t=z)
        cap_vpp_16 = h.ShieldedCapacitor(
            model="VPP_PERP_5"
        )(p=z, n=z, s=z, t=z)
        cap_vpp_17 = h.ShieldedCapacitor(
            model="VPP_PERP_6"
        )(p=z, n=z, s=z, t=z)
        cap_vpp_18 = h.ShieldedCapacitor(model="VPP_PERP_7")(
            p=z, n=z, s=z, t=z
        )
        cap_vpp_19 = h.ShieldedCapacitor(model="VPP_PERP_8")(
            p=z, n=z, s=z, t=z
        )
        cap_vpp_20 = h.ShieldedCapacitor(model="VPP_PERP_9")(
            p=z, n=z, s=z, t=z
        )
        cap_vpp_21 = h.ShieldedCapacitor(model="VPP_PERP_10")(
            p=z, n=z, s=z, t=z
        )

    return CapacitorPrimitives


# FIXME: How do I make this test less attrocious?


def _compile_and_test(prims: h.Module, paramtype: h.paramclass):

    # Compile
    sky130.compile(prims)

    # ... and Test
    for k in prims.namespace:
        if k is not "z":

            assert isinstance(prims.namespace[k], h.Instance)
            assert isinstance(prims.namespace[k].of, h.ExternalModuleCall)
            assert isinstance(prims.namespace[k].of.params, paramtype)


def test_compile():

    _compile_and_test(mos_primitives_module(), sky130.Sky130MosParams)
    _compile_and_test(genres_primitives_module(), sky130.Sky130GenResParams)
    _compile_and_test(precres_primitives_module(), sky130.Sky130PrecResParams)
    _compile_and_test(diode_primitives_module(), sky130.Sky130DiodeParams)
    _compile_and_test(bjt_primitives_module(), sky130.Sky130DeviceParams)
    _compile_and_test(mimcap_primitives_module(), sky130.Sky130MimParams)
    _compile_and_test(varcap_primitives_module(), sky130.Sky130VarParams)
    _compile_and_test(vppcap_primitives_module(), sky130.Sky130VPPParams)


def _netlist(prims):

    # Netlist it for the PDK
    sky130.compile(prims)
    h.netlist(prims, StringIO(), fmt="spice")
    h.netlist(prims, StringIO(), fmt="spectre")
    h.netlist(prims, StringIO(), fmt="verilog")


def test_netlist():

    _netlist(mos_primitives_module())
    _netlist(genres_primitives_module())
    _netlist(precres_primitives_module())
    _netlist(diode_primitives_module())
    _netlist(bjt_primitives_module())
    _netlist(mimcap_primitives_module())
    _netlist(varcap_primitives_module())
    _netlist(vppcap_primitives_module())


def test_mos_module():

    p = sky130.Sky130MosParams()

    @h.module
    class HasXtors:
        nfet_01v8 = s.sky130_fd_pr__nfet_01v8(p)()
        nfet_01v8_lvt = s.sky130_fd_pr__nfet_01v8_lvt(p)()
        pfet_01v8 = s.sky130_fd_pr__pfet_01v8(p)()
        pfet_01v8_hvt = s.sky130_fd_pr__pfet_01v8_hvt(p)()
        pfet_01v8_lvt = s.sky130_fd_pr__pfet_01v8_lvt(p)()
        pfet_g5v0d10v5 = s.sky130_fd_pr__pfet_g5v0d10v5(p)()
        nfet_g5v0d10v5 = s.sky130_fd_pr__nfet_g5v0d10v5(p)()
        pfet_g5v0d16v0 = s.sky130_fd_pr__pfet_g5v0d16v0(p)()
        nfet_20v0 = s.sky130_fd_pr__nfet_20v0(p)()
        nfet_20v0_zvt = s.sky130_fd_pr__nfet_20v0_zvt(p)()
        nfet_20v0_iso = s.sky130_fd_pr__nfet_20v0_iso(p)()
        pfet_20v0 = s.sky130_fd_pr__pfet_20v0(p)()
        nfet_03v3_nvt = s.sky130_fd_pr__nfet_03v3_nvt(p)()
        nfet_05v0_nvt = s.sky130_fd_pr__nfet_05v0_nvt(p)()
        nfet_20v0_nvt = s.sky130_fd_pr__nfet_20v0_nvt(p)()
        esd_nfet_01v8 = s.sky130_fd_pr__esd_nfet_01v8(p)()
        esd_nfet_g5v0d10v5 = s.sky130_fd_pr__esd_nfet_g5v0d10v5(p)()
        esd_nfet_g5v0d10v5_nvt = s.sky130_fd_pr__esd_nfet_g5v0d10v5_nvt(p)()
        esd_pfet_g5v0d10v5 = s.sky130_fd_pr__esd_pfet_g5v0d10v5(p)()


def test_genres_module():

    p = sky130.Sky130GenResParams()

    @h.module
    class HasGenRes:
        res_gen_po = s.sky130_fd_pr__res_generic_po(p)()
        res_gen_li = s.sky130_fd_pr__res_generic_l1(p)()
        res_gen_m1 = s.sky130_fd_pr__res_generic_m1(p)()
        res_gen_m2 = s.sky130_fd_pr__res_generic_m2(p)()
        res_gen_m3 = s.sky130_fd_pr__res_generic_m3(p)()
        res_gen_m4 = s.sky130_fd_pr__res_generic_m4(p)()
        res_gen_m5 = s.sky130_fd_pr__res_generic_m5(p)()
        res_gen_nd = s.sky130_fd_pr__res_generic_nd(p)()
        res_gen_pd = s.sky130_fd_pr__res_generic_pd(p)()
        res_gen_iso_pw = s.sky130_fd_pr__res_iso_pw(p)()


def test_precres_module():

    p = sky130.Sky130PrecResParams()

    @h.module
    class HasPrecRes:
        res_p_prec_035 = s.sky130_fd_pr__res_high_po_0p35(p)()
        res_p_prec_069 = s.sky130_fd_pr__res_high_po_0p69(p)()
        res_p_prec_141 = s.sky130_fd_pr__res_high_po_1p41(p)()
        res_p_prec_285 = s.sky130_fd_pr__res_high_po_2p85(p)()
        res_p_prec_530 = s.sky130_fd_pr__res_high_po_5p3(p)()
        res_p_minus_prec_035 = s.sky130_fd_pr__res_xhigh_po_0p35(p)()
        res_p_minus_prec_069 = s.sky130_fd_pr__res_xhigh_po_0p69(p)()
        res_p_minus_prec_141 = s.sky130_fd_pr__res_xhigh_po_1p41(p)()
        res_p_minus_prec_285 = s.sky130_fd_pr__res_xhigh_po_2p85(p)()
        res_p_minus_prec_530 = s.sky130_fd_pr__res_xhigh_po_5p3(p)()


def test_diode_module():

    p = sky130.Sky130DiodeParams()

    @h.module
    class HasDiodes:
        pwnd_55v = s.sky130_fd_pr__diode_pw2nd_05v5(p)()
        pwnd_110v = s.sky130_fd_pr__diode_pw2nd_11v0(p)()
        nat_pwnd_55v = s.sky130_fd_pr__diode_pw2nd_05v5_nvt(p)()
        lvt_pwnd_55v = s.sky130_fd_pr__diode_pw2nd_05v5_lvt(p)()
        pdnw_55v = s.sky130_fd_pr__diode_pd2nw_05v5(p)()
        pdnw_110v = s.sky130_fd_pr__diode_pd2nw_11v0(p)()
        hvt_pdnw_55v = s.sky130_fd_pr__diode_pd2nw_05v5_hvt(p)()
        lvt_pdnw_55v = s.sky130_fd_pr__diode_pd2nw_05v5_lvt(p)()
        px_rf_psnw = s.sky130_fd_pr__model__parasitic__rf_diode_ps2nw(p)()
        px_rf_pwdn = s.sky130_fd_pr__model__parasitic__rf_diode_pw2dn(p)()
        px_pwdn = s.sky130_fd_pr__model__parasitic__diode_pw2dn(p)()
        px_psdn = s.sky130_fd_pr__model__parasitic__diode_ps2dn(p)()
        px_psnw = s.sky130_fd_pr__model__parasitic__diode_ps2nw(p)()


def test_bjt_module():

    p = sky130.Sky130DeviceParams()

    @h.module
    class HasBJTs:

        npn_50v = s.sky130_fd_pr__npn_05v5(p)()
        npn_110v = s.sky130_fd_pr__npn_11v0(p)()
        pnp_50v = s.sky130_fd_pr__pnp_05v5(p)()


def test_gencap_module():

    p = sky130.Sky130MimParams()
    q = sky130.Sky130VarParams()

    @h.module
    class HasGenCaps:

        MIM_M3 = s.sky130_fd_pr__cap_mim_m3__base(p)()
        MIM_M4 = s.sky130_fd_pr__cap_mim_m4__base(p)()
        VAR_LVT = s.sky130_fd_pr__cap_var_lvt(q)()
        VAR_HVT = s.sky130_fd_pr__cap_var_hvt(q)()


def test_devcap_module():

    p = sky130.Sky130VPPParams()

    @h.module
    class HasDevCaps:

        cap_vpp_1 = s.sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield_o2(p)()
        cap_vpp_2 = s.sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield(p)()
        cap_vpp_3 = s.sky130_fd_pr__cap_vpp_08p6x07p8_m1m2_noshield(p)()
        cap_vpp_4 = s.sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield(p)()
        cap_vpp_5 = s.sky130_fd_pr__cap_vpp_11p5x11p7_m1m2_noshield(p)()
        cap_vpp_6 = s.sky130_fd_pr__cap_vpp_44p7x23p1_pol1m1m2m3m4m5_noshield(p)()
        cap_vpp_7 = s.sky130_fd_pr__cap_vpp_02p7x06p1_m1m2m3m4_shieldl1_fingercap(p)()
        cap_vpp_8 = s.sky130_fd_pr__cap_vpp_02p9x06p1_m1m2m3m4_shieldl1_fingercap2(p)()
        cap_vpp_9 = s.sky130_fd_pr__cap_vpp_02p7x11p1_m1m2m3m4_shieldl1_fingercap(p)()
        cap_vpp_10 = s.sky130_fd_pr__cap_vpp_02p7x21p1_m1m2m3m4_shieldl1_fingercap(p)()
        cap_vpp_11 = s.sky130_fd_pr__cap_vpp_02p7x41p1_m1m2m3m4_shieldl1_fingercap(p)()
        cap_vpp_12 = s.sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5(p)()
        cap_vpp_13 = s.sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldpom5(p)()
        cap_vpp_14 = s.sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3m4_shieldl1m5(p)()
        cap_vpp_15 = s.sky130_fd_pr__cap_vpp_04p4x04p6_m1m2m3_shieldl1m5_floatm4(p)()
        cap_vpp_16 = s.sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shieldl1m5_floatm4(p)()
        cap_vpp_17 = s.sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3_shieldl1m5_floatm4(p)()
        cap_vpp_18 = s.sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3_shieldm4(p)()
        cap_vpp_19 = s.sky130_fd_pr__cap_vpp_06p8x06p1_l1m1m2m3_shieldpom4(p)()
        cap_vpp_20 = s.sky130_fd_pr__cap_vpp_06p8x06p1_m1m2m3_shieldl1m4(p)()
        cap_vpp_21 = s.sky130_fd_pr__cap_vpp_11p3x11p8_l1m1m2m3m4_shieldm5(p)()

def test_walker_contents():
    from hdl21.tests.content import walker_test_content

    content = walker_test_content()
    sky130.compile(content)
