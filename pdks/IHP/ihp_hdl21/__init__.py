"""
IHP SG13G2 130nm BiCMOS PDK for Hdl21

This package provides Hdl21 integration for the IHP SG13G2 130nm BiCMOS PDK,
featuring high-performance SiGe HBTs with fT up to 350 GHz.

Usage:
    import hdl21 as h
    import ihp_hdl21

    # Create a module using generic primitives
    @h.module
    class MyInverter:
        vdd, vss, inp, out = h.Ports(4)
        p = h.Mos(tp=h.MosType.PMOS)(g=inp, d=out, s=vdd, b=vdd)
        n = h.Mos(tp=h.MosType.NMOS)(g=inp, d=out, s=vss, b=vss)

    # Compile to IHP technology
    ihp_hdl21.compile(MyInverter)
"""

from typing import Optional
from hdl21.pdk import register

# Grab our primary PDK-definition module
from . import pdk_logic
from .pdk_logic import *

# The optional external-data installation.
# Set by an instantiator of `Install`, if available.
install: Optional[Install] = None

# And register as a PDK module
register(pdk_logic)
