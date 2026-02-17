"""
Device dictionaries for IHP SG13G2 130nm BiCMOS PDK.

These dictionaries map Hdl21 primitive parameters to IHP-specific
ExternalModule instances representing the actual PDK devices.
"""

# Std-Lib Imports
from typing import Tuple, Dict
from dataclasses import dataclass, field

# Hdl21 Imports
import hdl21 as h
from hdl21.prefix import µ
from hdl21.primitives import (
    MosType,
    MosVth,
    MosFamily,
    MosParams,
    PhysicalResistorParams,
    PhysicalCapacitorParams,
    DiodeParams,
    BipolarParams,
)

# Local Imports
from ..pdk_data import *

# MOS transistor key: (name, MosType, MosVth, MosFamily)
MosKey = Tuple[str, MosType, MosVth, MosFamily]

# ============================================================================
# MOS Transistors
# ============================================================================
# IHP has 4 main MOS types:
# - sg13_lv_nmos/pmos: Low-voltage (1.2V core), min L=0.13µm
# - sg13_hv_nmos/pmos: High-voltage (3.3V I/O), min L=0.45µm

xtors: Dict[MosKey, h.ExternalModule] = {
    # Low-voltage NMOS (1.2V core)
    ("LV_NMOS", MosType.NMOS, MosVth.STD, MosFamily.CORE): xtor_module(
        "sg13_lv_nmos", params=IhpMosParams
    ),
    # Low-voltage PMOS (1.2V core)
    ("LV_PMOS", MosType.PMOS, MosVth.STD, MosFamily.CORE): xtor_module(
        "sg13_lv_pmos", params=IhpMosParams
    ),
    # High-voltage NMOS (3.3V I/O)
    ("HV_NMOS", MosType.NMOS, MosVth.STD, MosFamily.IO): xtor_module(
        "sg13_hv_nmos", params=IhpMosHvParams
    ),
    # High-voltage PMOS (3.3V I/O)
    ("HV_PMOS", MosType.PMOS, MosVth.STD, MosFamily.IO): xtor_module(
        "sg13_hv_pmos", params=IhpMosHvParams
    ),
}

# ============================================================================
# Bipolar Transistors (HBT and PNP)
# ============================================================================
# IHP's strength: high-performance SiGe HBTs with fT up to 350 GHz
# - npn13G2: Standard HBT (4 terminals: c, b, e, bn)
# - npn13G2l: Large HBT
# - npn13G2v: Variable emitter HBT
# - npn13G2_5t, npn13G2l_5t, npn13G2v_5t: 5-terminal variants
# - pnpMPA: Lateral PNP (3 terminals: c, b, e)

bjts: Dict[str, h.ExternalModule] = {
    # Standard 4-terminal HBTs
    "npn13G2": hbt_module("npn13G2", params=IhpHbtParams, num_terminals=4),
    "npn13G2l": hbt_module("npn13G2l", params=IhpHbtParams, num_terminals=4),
    "npn13G2v": hbt_module("npn13G2v", params=IhpHbtParams, num_terminals=4),
    # 5-terminal HBT variants (with temperature terminal)
    "npn13G2_5t": hbt_module("npn13G2_5t", params=IhpHbtParams, num_terminals=5),
    "npn13G2l_5t": hbt_module("npn13G2l_5t", params=IhpHbtParams, num_terminals=5),
    "npn13G2v_5t": hbt_module("npn13G2v_5t", params=IhpHbtParams, num_terminals=5),
    # Lateral PNP
    "pnpMPA": pnp_module("pnpMPA", params=IhpPnpParams),
}

# ============================================================================
# Resistors
# ============================================================================
# IHP resistors are 3-terminal devices (1, 2, bn - bulk node)
# - rsil: Silicided polysilicon (~7 ohm/sq)
# - rhigh: High-resistivity polysilicon (~1k ohm/sq)
# - rppd: P-doped polysilicon (~300 ohm/sq)

ress: Dict[str, h.ExternalModule] = {
    "rsil": res_module("rsil", numterminals=3, params=IhpResParams),
    "rhigh": res_module("rhigh", numterminals=3, params=IhpResParams),
    "rppd": res_module("rppd", numterminals=3, params=IhpResParams),
}

# ============================================================================
# Capacitors
# ============================================================================
# - cap_cmim: MIM capacitor (2-terminal: PLUS, MINUS)
# - cap_rfcmim: RF MIM capacitor (3-terminal: PLUS, MINUS, bn)
# - sg13_hv_svaricap: Varactor (4-terminal: G1, W, G2, bn)

caps: Dict[str, h.ExternalModule] = {
    "cap_cmim": cap_module("cap_cmim", numterminals=2, params=IhpCapParams),
    "cap_rfcmim": cap_module("cap_rfcmim", numterminals=3, params=IhpCapParams),
}

# Varactors (separate dict due to different terminal structure)
varicaps: Dict[str, h.ExternalModule] = {
    "sg13_hv_svaricap": varicap_module("sg13_hv_svaricap", params=IhpVaricapParams),
}

# ============================================================================
# Diodes and ESD Devices
# ============================================================================
# - schottky_nbl1: Schottky diode (3-terminal: A, C, S)
# - diodevdd_2kv/4kv, diodevss_2kv/4kv: ESD protection (3-terminal: VDD, PAD, VSS)

diodes: Dict[str, h.ExternalModule] = {
    "schottky_nbl1": schottky_module("schottky_nbl1", params=IhpDiodeParams),
}

esd_devices: Dict[str, h.ExternalModule] = {
    "diodevdd_2kv": esd_module("diodevdd_2kv", params=IhpEsdParams),
    "diodevdd_4kv": esd_module("diodevdd_4kv", params=IhpEsdParams),
    "diodevss_2kv": esd_module("diodevss_2kv", params=IhpEsdParams),
    "diodevss_4kv": esd_module("diodevss_4kv", params=IhpEsdParams),
}

# ============================================================================
# Module-Scope Cache
# ============================================================================
# Cache for ExternalModuleCall instances to avoid duplicate instantiation


@dataclass
class Cache:
    """Module-scope cache for device calls."""

    mos_modcalls: Dict[MosParams, h.ExternalModuleCall] = field(default_factory=dict)
    res_modcalls: Dict[PhysicalResistorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )
    cap_modcalls: Dict[PhysicalCapacitorParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )
    diode_modcalls: Dict[DiodeParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )
    bjt_modcalls: Dict[BipolarParams, h.ExternalModuleCall] = field(
        default_factory=dict
    )


CACHE = Cache()

# ============================================================================
# Default Device Sizes
# ============================================================================
# Default W/L values for devices when not explicitly specified

# MOS transistor defaults (w, l) in microns
default_xtor_size = {
    # LV devices: min L = 0.13µm
    "sg13_lv_nmos": (0.35 * µ, 0.13 * µ),
    "sg13_lv_pmos": (0.35 * µ, 0.13 * µ),
    # HV devices: min L = 0.45µm
    "sg13_hv_nmos": (0.35 * µ, 0.45 * µ),
    "sg13_hv_pmos": (0.35 * µ, 0.45 * µ),
}

# Resistor defaults (w, l) in microns
default_res_size = {
    "rsil": (0.5 * µ, 2.0 * µ),
    "rhigh": (0.5 * µ, 2.0 * µ),
    "rppd": (0.5 * µ, 2.0 * µ),
}

# Capacitor defaults (w, l) in microns
default_cap_size = {
    "cap_cmim": (6.0 * µ, 6.0 * µ),
    "cap_rfcmim": (6.0 * µ, 6.0 * µ),
    "sg13_hv_svaricap": (1.0 * µ, 1.0 * µ),
}
