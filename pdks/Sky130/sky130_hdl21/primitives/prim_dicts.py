from ..pdk_data import *

# Individuate component types
MosKey = Tuple[str, MosType, MosVth, MosFamily]

"""
These dictionaries are used to map all of the devices of the Sky130 technology
to their corresponding caller functions above. Keys and names are used to 
differentiate individual components and populate a namespace which can be used
to find and determine the correct internal device to use.
"""

xtors: Dict[MosKey, h.ExternalModule] = {
    # Add all generic transistors
    ("NMOS_1p8V_STD", MosType.NMOS, MosVth.STD, MosFamily.CORE): xtor_module(
        "sky130_fd_pr__nfet_01v8"
    ),
    ("NMOS_1p8V_LOW", MosType.NMOS, MosVth.LOW, MosFamily.CORE): xtor_module(
        "sky130_fd_pr__nfet_01v8_lvt"
    ),
    ("PMOS_1p8V_STD", MosType.PMOS, MosVth.STD, MosFamily.CORE): xtor_module(
        "sky130_fd_pr__pfet_01v8"
    ),
    ("PMOS_1p8V_HIGH", MosType.PMOS, MosVth.HIGH, MosFamily.CORE): xtor_module(
        "sky130_fd_pr__pfet_01v8_hvt"
    ),
    ("PMOS_1p8V_LOW", MosType.PMOS, MosVth.LOW, MosFamily.CORE): xtor_module(
        "sky130_fd_pr__pfet_01v8_lvt"
    ),
    ("PMOS_5p5V_D10_STD", MosType.PMOS, MosVth.STD, MosFamily.IO): xtor_module(
        "sky130_fd_pr__pfet_g5v0d10v5"
    ),
    ("NMOS_5p5V_D10_STD", MosType.NMOS, MosVth.STD, MosFamily.IO): xtor_module(
        "sky130_fd_pr__nfet_g5v0d10v5"
    ),
    ("PMOS_5p5V_D16_STD", MosType.PMOS, MosVth.STD, MosFamily.IO): xtor_module(
        "sky130_fd_pr__pfet_g5v0d16v0"
    ),
    ("NMOS_20p0V_STD", MosType.NMOS, MosVth.STD, MosFamily.NONE): xtor_module(
        "sky130_fd_pr__nfet_20v0", params=Sky130Mos20VParams
    ),
    ("NMOS_20p0V_LOW", MosType.NMOS, MosVth.ZERO, MosFamily.NONE): xtor_module(
        "sky130_fd_pr__nfet_20v0_zvt", params=Sky130Mos20VParams
    ),
    ("NMOS_ISO_20p0V", MosType.NMOS, MosVth.STD, MosFamily.NONE): xtor_module(
        "sky130_fd_pr__nfet_20v0_iso", params=Sky130Mos20VParams, num_terminals=5
    ),
    ("PMOS_20p0V", MosType.PMOS, MosVth.STD, MosFamily.NONE): xtor_module(
        "sky130_fd_pr__pfet_20v0", params=Sky130Mos20VParams
    ),
    # Note there are no NMOS HVT!
    # Add Native FET entries
    ("NMOS_3p3V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): xtor_module(
        "sky130_fd_pr__nfet_03v3_nvt"
    ),
    ("NMOS_5p0V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): xtor_module(
        "sky130_fd_pr__nfet_05v0_nvt"
    ),
    ("NMOS_20p0V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.NONE): xtor_module(
        "sky130_fd_pr__nfet_20v0_nvt", params=Sky130Mos20VParams
    ),
    # Add ESD FET entries
    ("ESD_NMOS_1p8V", MosType.NMOS, MosVth.STD, MosFamily.CORE): xtor_module(
        "sky130_fd_pr__esd_nfet_01v8"
    ),
    ("ESD_NMOS_5p5V_D10", MosType.NMOS, MosVth.STD, MosFamily.IO): xtor_module(
        "sky130_fd_pr__esd_nfet_g5v0d10v5"
    ),
    ("ESD_NMOS_5p5V_NAT", MosType.NMOS, MosVth.NATIVE, MosFamily.IO): xtor_module(
        "sky130_fd_pr__esd_nfet_g5v0d10v5_nvt"
    ),
    ("ESD_PMOS_5p5V", MosType.PMOS, MosVth.STD, MosFamily.IO): xtor_module(
        "sky130_fd_pr__esd_pfet_g5v0d10v5"
    ),
}

ress: Dict[str, h.ExternalModule] = {
    # 2-terminal generic resistors
    "GEN_PO": res_module(
        "sky130_fd_pr__res_generic_po",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_L1": res_module(
        "sky130_fd_pr__res_generic_l1",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M1": res_module(
        "sky130_fd_pr__res_generic_m1",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M2": res_module(
        "sky130_fd_pr__res_generic_m2",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M3": res_module(
        "sky130_fd_pr__res_generic_m3",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M4": res_module(
        "sky130_fd_pr__res_generic_m4",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    "GEN_M5": res_module(
        "sky130_fd_pr__res_generic_m5",
        2,
        Sky130GenResParams,
        spicetype=SpiceType.RESISTOR,
    ),
    # 3-terminal generic resistors
    "GEN_ND": res_module("sky130_fd_pr__res_generic_nd", 3, Sky130GenResParams),
    "GEN_PD": res_module("sky130_fd_pr__res_generic_pd", 3, Sky130GenResParams),
    "GEN_ISO_PW": res_module(
        "sky130_fd_pr__res_iso_pw",
        3,
        Sky130GenResParams,
    ),
    # 3-terminal precision resistors
    "PP_PREC_0p35": res_module(
        "sky130_fd_pr__res_high_po_0p35", 3, Sky130PrecResParams
    ),
    "PP_PREC_0p69": res_module(
        "sky130_fd_pr__res_high_po_0p69", 3, Sky130PrecResParams
    ),
    "PP_PREC_1p41": res_module(
        "sky130_fd_pr__res_high_po_1p41", 3, Sky130PrecResParams
    ),
    "PP_PREC_2p85": res_module(
        "sky130_fd_pr__res_high_po_2p85", 3, Sky130PrecResParams
    ),
    "PP_PREC_5p73": res_module(
        "sky130_fd_pr__res_high_po_5p73", 3, Sky130PrecResParams
    ),
    "PM_PREC_0p35": res_module(
        "sky130_fd_pr__res_xhigh_po_0p35", 3, Sky130PrecResParams
    ),
    "PM_PREC_0p69": res_module(
        "sky130_fd_pr__res_xhigh_po_0p69", 3, Sky130PrecResParams
    ),
    "PM_PREC_1p41": res_module(
        "sky130_fd_pr__res_xhigh_po_1p41", 3, Sky130PrecResParams
    ),
    "PM_PREC_2p85": res_module(
        "sky130_fd_pr__res_xhigh_po_2p85", 3, Sky130PrecResParams
    ),
    "PM_PREC_5p73": res_module(
        "sky130_fd_pr__res_xhigh_po_5p73", 3, Sky130PrecResParams
    ),
}

diodes: Dict[str, h.ExternalModule] = {
    # Add diodes
    "PWND_5p5V": diode_module("sky130_fd_pr__diode_pw2nd_05v5"),
    "PWND_11p0V": diode_module("sky130_fd_pr__diode_pw2nd_11v0"),
    "PWND_5p5V_NAT": diode_module("sky130_fd_pr__diode_pw2nd_05v5_nvt"),
    "PWND_5p5V_LVT": diode_module("sky130_fd_pr__diode_pw2nd_05v5_lvt"),
    "PDNW_5p5V": diode_module("sky130_fd_pr__diode_pd2nw_05v5"),
    "PDNW_11p0V": diode_module("sky130_fd_pr__diode_pd2nw_11v0"),
    "PDNW_5p5V_HVT": diode_module("sky130_fd_pr__diode_pd2nw_05v5_hvt"),
    "PDNW_5p5V_LVT": diode_module("sky130_fd_pr__diode_pd2nw_05v5_lvt"),
    "PX_RF_PSNW": diode_module("sky130_fd_pr__model__parasitic__rf_diode_ps2nw"),
    "PX_RF_PWDN": diode_module("sky130_fd_pr__model__parasitic__rf_diode_pw2dn"),
    "PX_PWDN": diode_module("sky130_fd_pr__model__parasitic__diode_pw2dn"),
    "PX_PSDN": diode_module("sky130_fd_pr__model__parasitic__diode_ps2dn"),
    "PX_PSNW": diode_module("sky130_fd_pr__model__parasitic__diode_ps2nw"),
}

"""
BJTs in this PDK are all subcircuits but are distributed in a way that is quite unusual
and can make it particularly difficult to access them without a PR to the PDK itself.

As noted here there is no functional difference between rf and non-rf BJTs in SKY130:

https://open-source-silicon.slack.com/archives/C016HUV935L/p1650549447460139?thread_ts=1650545374.248099&cid=C016HUV935L
"""
bjts: Dict[str, h.ExternalModule] = {
    # Add BJTs
    "NPN_5p0V_1x2": bjt_module("sky130_fd_pr__npn_05v5_W1p00L2p00", numterminals=4),
    "NPN_11p0V_1x1": bjt_module("sky130_fd_pr__npn_11v0_W1p00L1p00", numterminals=4),
    "NPN_5p0V_1x1": bjt_module("sky130_fd_pr__npn_05v5_W1p00L1p00", numterminals=4),
    "PNP_5p0V_0p68x0p68": bjt_module("sky130_fd_pr__pnp_05v5_W0p68L0p68"),
    "PNP_5p0V_3p40x3p40": bjt_module("sky130_fd_pr__pnp_05v5_W3p40L3p40"),
}

caps: Dict[str, h.ExternalModule] = {
    # List all MiM capacitors
    # https://open-source-silicon.slack.com/archives/C016HUV935L/p1618923323152300?thread_ts=1618887703.151600&cid=C016HUV935L
    "MIM_M3": cap_module(
        "sky130_fd_pr__cap_mim_m3_1",
        numterminals=2,
        params=Sky130MimParams,
    ),
    "MIM_M4": cap_module(
        "sky130_fd_pr__cap_mim_m3_2",
        numterminals=2,
        params=Sky130MimParams,
    ),
    # List available Varactors
    "VAR_LVT": cap_module(
        "sky130_fd_pr__cap_var_lvt",
        numterminals=3,
        params=Sky130VarParams,
    ),
    "VAR_HVT": cap_module(
        "sky130_fd_pr__cap_var_hvt",
        numterminals=3,
        params=Sky130VarParams,
    ),
}

vpps: Dict[str, h.ExternalModule] = {
    # List Parallel VPP capacitors
    "VPP_PARA_1": vpp_module("sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield_o2", 3),
    "VPP_PARA_2": vpp_module("sky130_fd_pr__cap_vpp_02p4x04p6_m1m2_noshield", 3),
    "VPP_PARA_3": vpp_module("sky130_fd_pr__cap_vpp_08p6x07p8_m1m2_noshield", 3),
    "VPP_PARA_4": vpp_module("sky130_fd_pr__cap_vpp_04p4x04p6_m1m2_noshield", 3),
    "VPP_PARA_5": vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_m1m2_noshield", 3),
    "VPP_PARA_6": vpp_module(
        "sky130_fd_pr__cap_vpp_44p7x23p1_pol1m1m2m3m4m5_noshield", 3
    ),
    "VPP_PARA_7": vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x06p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    "VPP_PARA_8": vpp_module(
        "sky130_fd_pr__cap_vpp_02p9x06p1_m1m2m3m4_shieldl1_fingercap2", 3
    ),
    "VPP_PARA_9": vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x11p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    "VPP_PARA_10": vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x21p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    "VPP_PARA_11": vpp_module(
        "sky130_fd_pr__cap_vpp_02p7x41p1_m1m2m3m4_shieldl1_fingercap", 3
    ),
    # List Perpendicular VPP capacitors
    "VPP_PERP_1": vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldm5", 4),
    "VPP_PERP_2": vpp_module(
        "sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3m4_shieldpom5", 4
    ),
    "VPP_PERP_3": vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3m4_shieldl1m5", 4),
    "VPP_PERP_4": vpp_module(
        "sky130_fd_pr__cap_vpp_04p4x04p6_m1m2m3_shieldl1m5_floatm4", 4
    ),
    "VPP_PERP_5": vpp_module(
        "sky130_fd_pr__cap_vpp_08p6x07p8_m1m2m3_shieldl1m5_floatm4", 4
    ),
    "VPP_PERP_6": vpp_module(
        "sky130_fd_pr__cap_vpp_11p5x11p7_m1m2m3_shieldl1m5_floatm4", 4
    ),
    "VPP_PERP_7": vpp_module("sky130_fd_pr__cap_vpp_11p5x11p7_l1m1m2m3_shieldm4", 4),
    "VPP_PERP_8": vpp_module("sky130_fd_pr__cap_vpp_06p8x06p1_l1m1m2m3_shieldpom4", 4),
    "VPP_PERP_9": vpp_module("sky130_fd_pr__cap_vpp_06p8x06p1_m1m2m3_shieldl1m4", 4),
    "VPP_PERP_10": vpp_module(
        "sky130_fd_pr__cap_vpp_11p3x11p8_l1m1m2m3m4_shieldm5_nhvtop", 4
    ),
}


@dataclass
class Cache:
    """# Module-Scope Cache(s)"""

    mos_modcalls: Dict[MosParams, h.ExternalModuleCall] = field(default_factory=dict)

    res_modcalls: Dict[PhysicalResistorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )

    cap_modcalls: Dict[PhysicalCapacitorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )

    diode_modcalls: Dict[DiodeParams, h.ExternalModule] = field(default_factory=dict)

    bjt_modcalls: Dict[BipolarParams, h.ExternalModule] = field(default_factory=dict)


CACHE = Cache()

"""
This section of code defines default sizes for various electronic components in the Sky130 technology,
including transistors, resistors, and capacitors. Default dimensions are provided in microns or PDK units,
with the sizes stored in dictionaries: default_xtor_size for transistors, default_gen_res_size for generic resistors,
default_prec_res_L for precise resistors, and default_cap_sizes for capacitors.
These default sizes are important for creating instances of the components with proper dimensions,
ensuring correct layout and performance in the circuit designs.
"""

# Default param dicts
default_xtor_size = {
    "sky130_fd_pr__nfet_01v8": (0.420 * µ, 0.150 * µ),
    "sky130_fd_pr__nfet_01v8_lvt": (
        0.420 * µ,
        0.150 * µ,
    ),
    "sky130_fd_pr__pfet_01v8": (0.550 * µ, 0.150 * µ),
    "sky130_fd_pr__pfet_01v8_hvt": (
        0.550 * µ,
        0.150 * µ,
    ),
    "sky130_fd_pr__pfet_01v8_lvt": (
        0.550 * µ,
        0.350 * µ,
    ),
    "sky130_fd_pr__pfet_g5v0d10v5": (
        0.420 * µ,
        0.500 * µ,
    ),
    "sky130_fd_pr__nfet_g5v0d10v5": (
        0.420 * µ,
        0.500 * µ,
    ),
    "sky130_fd_pr__pfet_g5v0d16v0": (
        5.000 * µ,
        0.660 * µ,
    ),
    "sky130_fd_pr__nfet_20v0": (29.410 * µ, 2.950 * µ),
    "sky130_fd_pr__nfet_20v0_zvt": (
        30.000 * µ,
        1.500 * µ,
    ),
    "sky130_fd_pr__nfet_20v0_iso": (
        30.000 * µ,
        1.500 * µ,
    ),
    "sky130_fd_pr__pfet_20v0": (30.000 * µ, 1.000 * µ),
    "sky130_fd_pr__nfet_03v3_nvt": (
        0.700 * µ,
        0.500 * µ,
    ),
    "sky130_fd_pr__nfet_05v0_nvt": (
        0.700 * µ,
        0.900 * µ,
    ),
    "sky130_fd_pr__nfet_20v0_nvt": (
        30.000 * µ,
        1.000 * µ,
    ),
    "sky130_fd_pr__esd_nfet_01v8": (
        20.350 * µ,
        0.165 * µ,
    ),
    "sky130_fd_pr__esd_nfet_g5v0d10v5": (
        14.500 * µ,
        0.550 * µ,
    ),
    "sky130_fd_pr__esd_nfet_g5v0d10v5_nvt": (
        10.000 * µ,
        0.900 * µ,
    ),
    "sky130_fd_pr__esd_pfet_g5v0d10v5": (
        14.500 * µ,
        0.550 * µ,
    ),
}

default_gen_res_size = {
    "sky130_fd_pr__res_generic_po": (
        0.720 * µ,
        0.290 * µ,
    ),
    "sky130_fd_pr__res_generic_l1": (
        0.720 * µ,
        0.290 * µ,
    ),
    "sky130_fd_pr__res_generic_m1": (
        0.720 * µ,
        0.290 * µ,
    ),
    "sky130_fd_pr__res_generic_m2": (
        0.720 * µ,
        0.290 * µ,
    ),
    "sky130_fd_pr__res_generic_m3": (
        0.720 * µ,
        0.290 * µ,
    ),
    "sky130_fd_pr__res_generic_m4": (
        0.720 * µ,
        0.290 * µ,
    ),
    "sky130_fd_pr__res_generic_m5": (
        0.720 * µ,
        0.290 * µ,
    ),
    "sky130_fd_pr__res_generic_nd": (
        0.150 * µ,
        0.270 * µ,
    ),
    "sky130_fd_pr__res_generic_pd": (
        0.150 * µ,
        0.270 * µ,
    ),
    # FIXME: This value is lifted from xschem but can't be found in documentation
    "sky130_fd_pr__res_iso_pw": (2.650 * µ, 2.650 * µ),
}

# These have to be left in microns for parsing reasons
default_prec_res_L = {
    "sky130_fd_pr__res_high_po_0p35": 0.350,
    "sky130_fd_pr__res_high_po_0p69": 0.690,
    "sky130_fd_pr__res_high_po_1p41": 1.410,
    "sky130_fd_pr__res_high_po_2p85": 2.850,
    "sky130_fd_pr__res_high_po_5p73": 5.300,
    "sky130_fd_pr__res_xhigh_po_0p35": 0.350,
    "sky130_fd_pr__res_xhigh_po_0p69": 0.690,
    "sky130_fd_pr__res_xhigh_po_1p41": 1.410,
    "sky130_fd_pr__res_xhigh_po_2p85": 2.850,
    "sky130_fd_pr__res_xhigh_po_5p73": 5.300,
}

default_cap_sizes = {
    # FIXME: Using documentation minimum sizing not sure of correct answer
    "sky130_fd_pr__cap_mim_m3_1": (
        2.000 * µ,
        2.000 * µ,
    ),
    "sky130_fd_pr__cap_mim_m3_2": (
        2.000 * µ,
        2.000 * µ,
    ),
    "sky130_fd_pr__cap_var_lvt": (0.180 * µ, 0.180 * µ),
    "sky130_fd_pr__cap_var_hvt": (0.180 * µ, 0.180 * µ),
}
