"""
IHP SG13G2 Digital Standard Cell Library

This module provides access to the IHP SG13G2 standard cell library.
The cells are organized in a single module since IHP provides one standard cell library.

Usage:
    from ihp_hdl21 import digital_cells
    from ihp_hdl21 import IhpLogicParams

    inv = digital_cells.inv_1(IhpLogicParams())
"""

from . import stdcells
from .stdcells import *
