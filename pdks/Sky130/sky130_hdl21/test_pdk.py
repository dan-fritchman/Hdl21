"""
# SkyWater 130nm OSS PDK Plug-In 

Unit Tests
"""

from io import StringIO
import hdl21 as h
from . import pdk_logic as sky130
import sky130_hdl21.primitives as s
from hdl21.prefix import µ
from hdl21.primitives import *


def test_default():
    h.pdk.set_default(sky130)
    assert h.pdk.default() is sky130


def mos_primitives_module():

    p = sky130.Sky130MosParams()

    @h.module
    class Primitives:
        """Module with all the non-20v FETs supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        # Add all generic transistors
        nfet_01v8 = h.Mos(tp=MosType.NMOS, vth=MosVth.STD, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )
        nfet_01v8_lvt = h.Mos(tp=MosType.NMOS, vth=MosVth.LOW, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )
        pfet_01v8 = h.Mos(tp=MosType.PMOS, vth=MosVth.STD, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )
        pfet_01v8_hvt = h.Mos(tp=MosType.PMOS, vth=MosVth.HIGH, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )
        pfet_01v8_lvt = h.Mos(tp=MosType.PMOS, vth=MosVth.LOW, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )
        pfet_g5v0d10v5 = h.Mos(tp=MosType.PMOS, vth=MosVth.STD, family=MosFamily.IO)(
            d=z, g=z, s=z, b=z
        )
        nfet_g5v0d10v5 = h.Mos(tp=MosType.NMOS, vth=MosVth.STD, family=MosFamily.IO)(
            d=z, g=z, s=z, b=z
        )
        pfet_g5v0d16v0 = h.Mos(tp=MosType.PMOS, vth=MosVth.STD, family=MosFamily.IO)(
            d=z, g=z, s=z, b=z
        )
        nfet_03v3_nvt = h.Mos(
            tp=MosType.NMOS, vth=MosVth.NATIVE, family=MosFamily.NONE
        )(d=z, g=z, s=z, b=z)
        nfet_05v0_nvt = h.Mos(
            tp=MosType.NMOS, vth=MosVth.NATIVE, family=MosFamily.NONE
        )(d=z, g=z, s=z, b=z)
        esd_nfet_01v8 = h.Mos(tp=MosType.NMOS, vth=MosVth.STD, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )
        esd_nfet_g5v0d10v5 = h.Mos(
            tp=MosType.NMOS, vth=MosVth.STD, family=MosFamily.IO
        )(d=z, g=z, s=z, b=z)
        esd_nfet_g5v0d10v5_nvt = h.Mos(
            tp=MosType.NMOS, vth=MosVth.NATIVE, family=MosFamily.IO
        )(d=z, g=z, s=z, b=z)
        esd_pfet_g5v0d10v5 = h.Mos(
            tp=MosType.PMOS, vth=MosVth.STD, family=MosFamily.IO
        )(d=z, g=z, s=z, b=z)

    return Primitives


def mos20v_primitives_module():
    @h.module
    class Primitives:
        """Module with all the 20v FETs supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        nfet_20v0 = h.Mos(model="NMOS_20p0V_STD")(d=z, g=z, s=z, b=z)
        nfet_20v0_zvt = h.Mos(model="NMOS_20p0V_LOW")(d=z, g=z, s=z, b=z)
        # nfet_20v0_iso = h.Mos(model="NMOS_ISO_20p0V")(d=z, g=z, s=z, b=z) <-- can't be compiled.
        pfet_20v0 = h.Mos(model="PMOS_20p0V")(d=z, g=z, s=z, b=z)
        nfet_20v0_nvt = h.Mos(model="NMOS_20p0V_NAT")(d=z, g=z, s=z, b=z)

    return Primitives


def genres_primitives_module():
    @h.module
    class ResistorPrimitives:
        """Module with all the generic resistor primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        res_gen_po = h.PhysicalResistor(model="GEN_PO")(p=z, n=z)
        res_gen_li = h.PhysicalResistor(model="GEN_L1")(p=z, n=z)
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

        res_p_prec_035 = h.ThreeTerminalResistor(model="PP_PREC_0p35")(p=z, n=z, b=z)
        res_p_prec_069 = h.ThreeTerminalResistor(model="PP_PREC_0p69")(p=z, n=z, b=z)
        res_p_prec_141 = h.ThreeTerminalResistor(model="PP_PREC_1p41")(p=z, n=z, b=z)
        res_p_prec_285 = h.ThreeTerminalResistor(model="PP_PREC_2p85")(p=z, n=z, b=z)
        res_p_prec_573 = h.ThreeTerminalResistor(model="PP_PREC_5p73")(p=z, n=z, b=z)

        res_p_minus_prec_035 = h.ThreeTerminalResistor(model="PM_PREC_0p35")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_069 = h.ThreeTerminalResistor(model="PM_PREC_0p69")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_141 = h.ThreeTerminalResistor(model="PM_PREC_1p41")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_285 = h.ThreeTerminalResistor(model="PM_PREC_2p85")(
            p=z, n=z, b=z
        )
        res_p_minus_prec_573 = h.ThreeTerminalResistor(model="PM_PREC_5p73")(
            p=z, n=z, b=z
        )

    return ResistorPrimitives


def diode_primitives_module():
    @h.module
    class DiodePrimitives:
        """Module with all the diode primitives supported by the PDK package"""

        z = h.Signal(desc="Sole signal connected to everything")

        pwnd_55v = h.Diode(model="PWND_5p5V")(p=z, n=z)
        pwnd_110v = h.Diode(model="PWND_11p0V")(p=z, n=z)
        nat_pwnd_55v = h.Diode(model="PWND_5p5V_NAT")(p=z, n=z)
        lvt_pwnd_55v = h.Diode(model="PWND_5p5V_LVT")(p=z, n=z)
        pdnw_55v = h.Diode(model="PDNW_5p5V")(p=z, n=z)
        pdnw_110v = h.Diode(model="PDNW_11p0V")(p=z, n=z)
        hvt_pdnw_55v = h.Diode(model="PDNW_5p5V_HVT")(p=z, n=z)
        lvt_pdnw_55v = h.Diode(model="PDNW_5p5V_LVT")(p=z, n=z)
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

        # No compilation support for these yet
        # npn_5_1x2  = h.Npn(model = "NPN_5p0V_1x2")(e=z, b=z, c=z, s=z)
        # npn_11_1x1 = h.Npn(model = "NPN_11p0V_1x1")(e=z, b=z, c=z, s=z)
        # npn_5_1x1  = h.Npn(model = "NPN_5p0V_1x1")(e=z, b=z, c=z, s=z)
        pnp_5_1x1 = h.Pnp(model="PNP_5p0V_0p68x0p68")(e=z, b=z, c=z)
        pnp_5_3x3 = h.Pnp(model="PNP_5p0V_3p40x3p40")(e=z, b=z, c=z)

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


def _compile_and_test(prims: h.Module, paramtype: h.paramclass):

    # Compile
    sky130.compile(prims)

    # ... and Test
    for k in prims.namespace:
        if k != "z":

            assert isinstance(prims.namespace[k], h.Instance)
            assert isinstance(prims.namespace[k].of, h.ExternalModuleCall)
            assert isinstance(prims.namespace[k].of.params, paramtype)


def test_compile():

    _compile_and_test(mos_primitives_module(), sky130.Sky130MosParams)
    _compile_and_test(mos20v_primitives_module(), sky130.Sky130Mos20VParams)
    _compile_and_test(genres_primitives_module(), sky130.Sky130GenResParams)
    _compile_and_test(precres_primitives_module(), sky130.Sky130PrecResParams)
    _compile_and_test(diode_primitives_module(), sky130.Sky130DiodeParams)
    _compile_and_test(bjt_primitives_module(), sky130.Sky130BipolarParams)
    _compile_and_test(mimcap_primitives_module(), sky130.Sky130MimParams)
    _compile_and_test(varcap_primitives_module(), sky130.Sky130VarParams)


def _netlist(prims):

    # Netlist it for the PDK
    sky130.compile(prims)
    h.netlist(prims, StringIO(), fmt="spice")

    # FIXME: The following netlist formats are not yet supported
    # h.netlist(prims, StringIO(), fmt="spectre")
    # h.netlist(prims, StringIO(), fmt="verilog")


def test_netlist():

    _netlist(mos_primitives_module())
    _netlist(mos20v_primitives_module())
    _netlist(genres_primitives_module())
    _netlist(precres_primitives_module())
    _netlist(diode_primitives_module())
    _netlist(bjt_primitives_module())
    _netlist(mimcap_primitives_module())
    _netlist(varcap_primitives_module())


def test_mos_module():

    p = sky130.Sky130MosParams()
    q = sky130.Sky130Mos20VParams()

    @h.module
    class HasXtors:
        nfet_01v8 = s.NMOS_1p8V_STD(p)()
        nfet_01v8_lvt = s.NMOS_1p8V_LOW(p)()
        pfet_01v8 = s.PMOS_1p8V_STD(p)()
        pfet_01v8_hvt = s.PMOS_1p8V_HIGH(p)()
        pfet_01v8_lvt = s.PMOS_1p8V_LOW(p)()
        pfet_g5v0d10v5 = s.PMOS_5p5V_D10_STD(p)()
        nfet_g5v0d10v5 = s.NMOS_5p5V_D10_STD(p)()
        pfet_g5v0d16v0 = s.PMOS_5p5V_D16_STD(p)()
        nfet_20v0 = s.NMOS_20p0V_STD(q)()
        nfet_20v0_zvt = s.NMOS_20p0V_LOW(q)()
        nfet_20v0_iso = s.NMOS_ISO_20p0V(q)()
        pfet_20v0 = s.PMOS_20p0V(q)()
        nfet_03v3_nvt = s.NMOS_3p3V_NAT(p)()
        nfet_05v0_nvt = s.NMOS_5p0V_NAT(p)()
        nfet_20v0_nvt = s.NMOS_20p0V_NAT(q)()
        esd_nfet_01v8 = s.ESD_NMOS_1p8V(p)()
        esd_nfet_g5v0d10v5 = s.ESD_NMOS_5p5V_D10(p)()
        esd_nfet_g5v0d10v5_nvt = s.ESD_NMOS_5p5V_NAT(p)()
        esd_pfet_g5v0d10v5 = s.ESD_PMOS_5p5V(p)()


def test_genres_module():

    p = sky130.Sky130GenResParams()

    @h.module
    class HasGenRes:
        res_gen_po = s.GEN_PO(p)()
        res_gen_l1 = s.GEN_L1(p)()
        res_gen_m1 = s.GEN_M1(p)()
        res_gen_m2 = s.GEN_M2(p)()
        res_gen_m3 = s.GEN_M3(p)()
        res_gen_m4 = s.GEN_M4(p)()
        res_gen_m5 = s.GEN_M5(p)()
        res_gen_nd = s.GEN_ND(p)()
        res_gen_pd = s.GEN_PD(p)()
        res_gen_iso_pw = s.GEN_ISO_PW(p)()


def test_precres_module():

    p = sky130.Sky130PrecResParams()

    @h.module
    class HasPrecRes:
        res_p_prec_035 = s.PP_PREC_0p35(p)()
        res_p_prec_069 = s.PP_PREC_0p69(p)()
        res_p_prec_141 = s.PP_PREC_1p41(p)()
        res_p_prec_285 = s.PP_PREC_2p85(p)()
        res_p_prec_573 = s.PP_PREC_5p73(p)()
        res_p_minus_prec_035 = s.PM_PREC_0p35(p)()
        res_p_minus_prec_069 = s.PM_PREC_0p69(p)()
        res_p_minus_prec_141 = s.PM_PREC_1p41(p)()
        res_p_minus_prec_285 = s.PM_PREC_2p85(p)()
        res_p_minus_prec_573 = s.PM_PREC_5p73(p)()


def test_diode_module():

    p = sky130.Sky130DiodeParams()

    @h.module
    class HasDiodes:
        pwnd_55v = s.PWND_5p5V(p)()
        pwnd_110v = s.PWND_11p0V(p)()
        nat_pwnd_55v = s.PWND_5p5V_NAT(p)()
        lvt_pwnd_55v = s.PWND_5p5V_LVT(p)()
        pdnw_55v = s.PDNW_5p5V(p)()
        pdnw_110v = s.PDNW_11p0V(p)()
        hvt_pdnw_55v = s.PDNW_5p5V_HVT(p)()
        lvt_pdnw_55v = s.PDNW_5p5V_LVT(p)()
        px_rf_psnw = s.PX_RF_PSNW(p)()
        px_rf_pwdn = s.PX_RF_PWDN(p)()
        px_pwdn = s.PX_PWDN(p)()
        px_psdn = s.PX_PSDN(p)()
        px_psnw = s.PX_PSNW(p)()


def test_bjt_module():

    p = sky130.Sky130BipolarParams()

    @h.module
    class HasBJTs:

        npn_5_1x2 = s.NPN_5p0V_1x2(p)()
        npn_11_1x1 = s.NPN_11p0V_1x1(p)()
        npn_5_1x1 = s.NPN_5p0V_1x1(p)()
        pnp_5_1x1 = s.PNP_5p0V_0p68x0p68(p)()
        pnp_5_3x3 = s.PNP_5p0V_3p40x3p40(p)()


def test_gencap_module():

    p = sky130.Sky130MimParams()
    q = sky130.Sky130VarParams()

    @h.module
    class HasGenCaps:

        MIM_M3 = s.MIM_M3(p)()
        MIM_M4 = s.MIM_M4(p)()
        VAR_LVT = s.VAR_LVT(q)()
        VAR_HVT = s.VAR_HVT(q)()


def test_devcap_module():

    p = sky130.Sky130VPPParams()

    @h.module
    class HasDevCaps:

        cap_vpp_1 = s.VPP_PARA_1(p)()
        cap_vpp_2 = s.VPP_PARA_2(p)()
        cap_vpp_3 = s.VPP_PARA_3(p)()
        cap_vpp_4 = s.VPP_PARA_4(p)()
        cap_vpp_5 = s.VPP_PARA_5(p)()
        cap_vpp_6 = s.VPP_PARA_6(p)()
        cap_vpp_7 = s.VPP_PARA_7(p)()
        cap_vpp_8 = s.VPP_PARA_8(p)()
        cap_vpp_9 = s.VPP_PARA_9(p)()
        cap_vpp_10 = s.VPP_PARA_10(p)()
        cap_vpp_11 = s.VPP_PARA_11(p)()
        cap_vpp_12 = s.VPP_PERP_1(p)()
        cap_vpp_13 = s.VPP_PERP_2(p)()
        cap_vpp_14 = s.VPP_PERP_3(p)()
        cap_vpp_15 = s.VPP_PERP_4(p)()
        cap_vpp_16 = s.VPP_PERP_5(p)()
        cap_vpp_17 = s.VPP_PERP_6(p)()
        cap_vpp_18 = s.VPP_PERP_7(p)()
        cap_vpp_19 = s.VPP_PERP_8(p)()
        cap_vpp_20 = s.VPP_PERP_9(p)()
        cap_vpp_21 = s.VPP_PERP_10(p)()


def test_walker_contents():
    from hdl21.tests.content import walker_test_content

    content = walker_test_content()
    sky130.compile(content)
