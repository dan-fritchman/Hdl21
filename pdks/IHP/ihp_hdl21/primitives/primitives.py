"""
IHP SG13G2 Primitive Device Definitions

This module provides direct access to IHP PDK devices as ExternalModules.
Use these for explicit device instantiation when you need full control
over the device type, bypassing the automatic primitive conversion.

Example:
    from ihp_hdl21.primitives import LV_NMOS, NPN13G2

    @h.module
    class MyCircuit:
        vdd, vss, inp, out = h.Ports(4)
        n = LV_NMOS(IhpMosParams(w=1.0, l=0.13))(d=out, g=inp, s=vss, b=vss)
"""

from ..pdk_data import *

# ============================================================================
# MOS Transistors
# ============================================================================

# Low-voltage (1.2V core) transistors - min L = 0.13µm
LV_NMOS = xtor_module("sg13_lv_nmos", params=IhpMosParams)
LV_PMOS = xtor_module("sg13_lv_pmos", params=IhpMosParams)

# High-voltage (3.3V I/O) transistors - min L = 0.45µm
HV_NMOS = xtor_module("sg13_hv_nmos", params=IhpMosHvParams)
HV_PMOS = xtor_module("sg13_hv_pmos", params=IhpMosHvParams)

# ============================================================================
# Bipolar Transistors - HBT (SiGe:C npn-HBT)
# ============================================================================
# High-performance HBTs with fT up to 350 GHz, fmax up to 450 GHz

# Standard 4-terminal HBTs (c, b, e, bn)
NPN13G2 = hbt_module("npn13G2", params=IhpHbtParams, num_terminals=4)
NPN13G2L = hbt_module("npn13G2l", params=IhpHbtParams, num_terminals=4)
NPN13G2V = hbt_module("npn13G2v", params=IhpHbtParams, num_terminals=4)

# 5-terminal HBT variants (c, b, e, bn, t)
NPN13G2_5T = hbt_module("npn13G2_5t", params=IhpHbtParams, num_terminals=5)
NPN13G2L_5T = hbt_module("npn13G2l_5t", params=IhpHbtParams, num_terminals=5)
NPN13G2V_5T = hbt_module("npn13G2v_5t", params=IhpHbtParams, num_terminals=5)

# ============================================================================
# Bipolar Transistors - Lateral PNP
# ============================================================================

# Lateral PNP transistor (3-terminal: c, b, e)
PNPMPA = pnp_module("pnpMPA", params=IhpPnpParams)

# ============================================================================
# Resistors (3-terminal with bulk connection)
# ============================================================================

# Silicided polysilicon resistor (~7 ohm/sq)
RSIL = res_module("rsil", numterminals=3, params=IhpResParams)

# High-resistivity polysilicon resistor (~1k ohm/sq)
RHIGH = res_module("rhigh", numterminals=3, params=IhpResParams)

# P-doped polysilicon resistor (~300 ohm/sq)
RPPD = res_module("rppd", numterminals=3, params=IhpResParams)

# ============================================================================
# Capacitors
# ============================================================================

# MIM capacitor (2-terminal: PLUS, MINUS)
CAP_CMIM = cap_module("cap_cmim", numterminals=2, params=IhpCapParams)

# RF MIM capacitor (3-terminal: PLUS, MINUS, bn)
CAP_RFCMIM = cap_module("cap_rfcmim", numterminals=3, params=IhpCapParams)

# Varactor (4-terminal: G1, W, G2, bn)
SVARICAP = varicap_module("sg13_hv_svaricap", params=IhpVaricapParams)

# ============================================================================
# Diodes
# ============================================================================

# Schottky diode (3-terminal: A, C, S)
SCHOTTKY_NBL1 = schottky_module("schottky_nbl1", params=IhpDiodeParams)

# ============================================================================
# ESD Protection Devices (3-terminal: VDD, PAD, VSS)
# ============================================================================

DIODEVDD_2KV = esd_module("diodevdd_2kv", params=IhpEsdParams)
DIODEVDD_4KV = esd_module("diodevdd_4kv", params=IhpEsdParams)
DIODEVSS_2KV = esd_module("diodevss_2kv", params=IhpEsdParams)
DIODEVSS_4KV = esd_module("diodevss_4kv", params=IhpEsdParams)
