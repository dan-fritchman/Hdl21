from ..pdk_data import *

# Individuate component types
MosKey = Tuple[str, h.MosType]
BjtKey = Tuple[str, h.BipolarType]

xtors: Dict[MosKey, h.ExternalModule] = {
    ("PFET_3p3V", MosType.PMOS, MosFamily.CORE): xtor_module("pfet_03v3"),
    ("NFET_3p3V", MosType.NMOS, MosFamily.CORE): xtor_module("nfet_03v3"),
    ("NFET_6p0V", MosType.NMOS, MosFamily.IO): xtor_module("nfet_06v0"),
    ("PFET_6p0V", MosType.PMOS, MosFamily.IO): xtor_module("pfet_06v0"),
    ("NFET_3p3V_DSS", MosType.NMOS, MosFamily.NONE): xtor_module("nfet_03v3_dss"),
    ("PFET_3p3V_DSS", MosType.PMOS, MosFamily.NONE): xtor_module("pfet_03v3_dss"),
    ("NFET_6p0V_DSS", MosType.NMOS, MosFamily.NONE): xtor_module("nfet_06v0_dss"),
    ("PFET_6p0V_DSS", MosType.PMOS, MosFamily.NONE): xtor_module("pfet_06v0_dss"),
    ("NFET_6p0V_NAT", MosType.NMOS, MosFamily.NONE): xtor_module("nfet_06v0_nvt"),
}

ress: Dict[str, h.ExternalModule] = {
    "NPLUS_U": res_module("nplus_u", 3),
    "PPLUS_U": res_module("pplus_u", 3),
    "NPLUS_S": res_module("nplus_s", 3),
    "PPLUS_S": res_module("pplus_s", 3),
    "NWELL": res_module("nwell", 3),
    "NPOLYF_U": res_module("npolyf_u", 3),
    "PPOLYF_U": res_module("ppolyf_u", 3),
    "NPOLYF_S": res_module("npolyf_s", 3),
    "PPOLYF_S": res_module("ppolyf_s", 3),
    "PPOLYF_U_1K": res_module("ppolyf_u_1k", 3),
    "PPOLYF_U_2K": res_module("ppolyf_u_2k", 3),
    "PPOLYF_U_1K_6P0": res_module("ppolyf_u_1k_6p0", 3),
    "PPOLYF_U_2K_6P0": res_module("ppolyf_u_2k_6p0", 3),
    "PPOLYF_U_3K": res_module("ppolyf_u_3k", 3),
    "RM1": res_module("rm1", 2),
    "RM2": res_module("rm2", 2),
    "RM3": res_module("rm3", 2),
    "TM6K": res_module("tm6k", 2),
    "TM9K": res_module("tm9k", 2),
    "TM11K": res_module("tm11k", 2),
    "TM30K": res_module("tm30k", 2),
}

diodes: Dict[str, h.ExternalModule] = {
    "ND2PS_3p3V": diode_module("diode_nd2ps_03v3"),
    "PD2NW_3p3V": diode_module("diode_pd2nw_03v3"),
    "ND2PS_6p0V": diode_module("diode_nd2ps_06v0"),
    "PD2NW_6p0V": diode_module("diode_pd2nw_06v0"),
    "NW2PS_3p3V": diode_module("diode_nw2ps_03v3"),
    "NW2PS_6p0V": diode_module("diode_nw2ps_06v0"),
    "PW2DW": diode_module("diode_pw2dw"),
    "DW2PS": diode_module("diode_dw2ps"),
    "Schottky": diode_module("sc_diode"),
}

bjts: Dict[BjtKey, h.ExternalModule] = {
    "PNP_10p0x0p42": bjt_module("pnp_10p00x00p42"),
    "PNP_5p0x0p42": bjt_module("pnp_05p00x00p42"),
    "PNP_10p0x10p0": bjt_module("pnp_10p00x10p00"),
    "PNP_5p0x5p0": bjt_module("pnp_05p00x05p00"),
    "NPN_10p0x10p0": bjt_module("npn_10p00x10p00", 4),
    "NPN_5p0x5p0": bjt_module("npn_05p00x05p00", 4),
    "NPN_0p54x16p0": bjt_module("npn_00p54x16p00", 4),
    "NPN_0p54x8p0": bjt_module("npn_00p54x08p00", 4),
    "NPN_0p54x4p0": bjt_module("npn_00p54x04p00", 4),
    "NPN_0p54x2p0": bjt_module("npn_00p54x02p00", 4),
}

caps: Dict[str, h.ExternalModule] = {
    "MIM_1p5fF": cap_module("cap_mim_1f5fF", GF180CapParams),
    "MIM_1p0fF": cap_module("cap_mim_1f0fF", GF180CapParams),
    "MIM_2p0fF": cap_module("cap_mim_2f0fF", GF180CapParams),
    "PMOS_3p3V": cap_module("cap_pmos_03v3", GF180CapParams),
    "NMOS_6p0V": cap_module("cap_nmos_06v0", GF180CapParams),
    "PMOS_6p0V": cap_module("cap_pmos_06v0", GF180CapParams),
    "NMOS_3p3V": cap_module("cap_nmos_03v3", GF180CapParams),
    "NMOS_Nwell_3p3V": cap_module("cap_nmos_03v3_b", GF180CapParams),
    "PMOS_Pwell_3p3V": cap_module("cap_pmos_03v3_b", GF180CapParams),
    "NMOS_Nwell_6p0V": cap_module("cap_nmos_06v0_b", GF180CapParams),
    "PMOS_Pwell_6p0V": cap_module("cap_pmos_06v0_b", GF180CapParams),
}

default_xtor_size = {
    "pfet_03v3": (0.220 * µ, 0.280 * µ),
    "nfet_03v3": (0.220 * µ, 0.280 * µ),
    "nfet_06v0": (0.300 * µ, 0.700 * µ),
    "pfet_06v0": (0.300 * µ, 0.500 * µ),
    "nfet_03v3_dss": (0.220 * µ, 0.280 * µ),
    "pfet_03v3_dss": (0.220 * µ, 0.280 * µ),
    "nfet_06v0_dss": (0.300 * µ, 0.500 * µ),
    "pfet_06v0_dss": (0.300 * µ, 0.500 * µ),
    "nfet_06v0_nvt": (0.800 * µ, 1.800 * µ),
}

default_res_size = {
    "nplus_u": (1 * µ, 1 * µ),
    "pplus_u": (1 * µ, 1 * µ),
    "nplus_s": (1 * µ, 1 * µ),
    "pplus_s": (1 * µ, 1 * µ),
    "nwell": (1 * µ, 1 * µ),
    "npolyf_u": (1 * µ, 1 * µ),
    "ppolyf_u": (1 * µ, 1 * µ),
    "npolyf_s": (1 * µ, 1 * µ),
    "ppolyf_s": (1 * µ, 1 * µ),
    "ppolyf_u_1k": (1 * µ, 1 * µ),
    "ppolyf_u_2k": (1 * µ, 1 * µ),
    "ppolyf_u_1k_6p0": (1 * µ, 1 * µ),
    "ppolyf_u_2k_6p0": (1 * µ, 1 * µ),
    "ppolyf_u_3k": (1 * µ, 1 * µ),
    "rm1": (1 * µ, 1 * µ),
    "rm2": (1 * µ, 1 * µ),
    "rm3": (1 * µ, 1 * µ),
    "tm6k": (1 * µ, 1 * µ),
    "tm9k": (1 * µ, 1 * µ),
    "tm11k": (1 * µ, 1 * µ),
    "tm30k": (1 * µ, 1 * µ),
}

default_diode_size = {
    "diode_nd2ps_03v3": (1 * µ, 1 * µ),
    "diode_pd2nw_03v3": (1 * µ, 1 * µ),
    "diode_nd2ps_06v0": (1 * µ, 1 * µ),
    "diode_pd2nw_06v0": (1 * µ, 1 * µ),
    "diode_nw2ps_03v3": (1 * µ, 1 * µ),
    "diode_nw2ps_06v0": (1 * µ, 1 * µ),
    "diode_pw2dw": (1 * µ, 1 * µ),
    "diode_dw2ps": (1 * µ, 1 * µ),
    "sc_diode": (1 * µ, 1 * µ),
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
