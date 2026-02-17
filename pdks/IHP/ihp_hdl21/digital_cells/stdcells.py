"""
IHP SG13G2 Standard Cell Library

This module defines all standard cells available in the IHP SG13G2 PDK.
Each cell is defined as an ExternalModule with the appropriate port list.

Generated from: IHP-Open-PDK/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice
"""

from ..pdk_data import logic_module

# ============================================================================
# Combinational Logic - AND-OR Gates
# ============================================================================

# A21O: 2-input AND into first input of 2-input OR
a21o_1 = logic_module(
    "sg13g2_a21o_1",
    "SG13G2 Standard Cell",
    ["X", "A1", "A2", "B1", "VDD", "VSS"],
)
a21o_2 = logic_module(
    "sg13g2_a21o_2",
    "SG13G2 Standard Cell",
    ["X", "A1", "A2", "B1", "VDD", "VSS"],
)

# A21OI: A21O with inverted output
a21oi_1 = logic_module(
    "sg13g2_a21oi_1",
    "SG13G2 Standard Cell",
    ["Y", "A1", "A2", "B1", "VDD", "VSS"],
)
a21oi_2 = logic_module(
    "sg13g2_a21oi_2",
    "SG13G2 Standard Cell",
    ["Y", "A1", "A2", "B1", "VDD", "VSS"],
)

# A221OI: (A1 & A2) | (B1 & B2) | C1, inverted
a221oi_1 = logic_module(
    "sg13g2_a221oi_1",
    "SG13G2 Standard Cell",
    ["Y", "A1", "A2", "B1", "B2", "C1", "VDD", "VSS"],
)

# A22OI: (A1 & A2) | (B1 & B2), inverted
a22oi_1 = logic_module(
    "sg13g2_a22oi_1",
    "SG13G2 Standard Cell",
    ["Y", "A1", "A2", "B1", "B2", "VDD", "VSS"],
)

# ============================================================================
# Combinational Logic - Basic Gates
# ============================================================================

# AND2: 2-input AND
and2_1 = logic_module(
    "sg13g2_and2_1",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "VDD", "VSS"],
)
and2_2 = logic_module(
    "sg13g2_and2_2",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "VDD", "VSS"],
)

# AND3: 3-input AND
and3_1 = logic_module(
    "sg13g2_and3_1",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "VDD", "VSS"],
)
and3_2 = logic_module(
    "sg13g2_and3_2",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "VDD", "VSS"],
)

# AND4: 4-input AND
and4_1 = logic_module(
    "sg13g2_and4_1",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "D", "VDD", "VSS"],
)
and4_2 = logic_module(
    "sg13g2_and4_2",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "D", "VDD", "VSS"],
)

# OR2: 2-input OR
or2_1 = logic_module(
    "sg13g2_or2_1",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "VDD", "VSS"],
)
or2_2 = logic_module(
    "sg13g2_or2_2",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "VDD", "VSS"],
)

# OR3: 3-input OR
or3_1 = logic_module(
    "sg13g2_or3_1",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "VDD", "VSS"],
)
or3_2 = logic_module(
    "sg13g2_or3_2",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "VDD", "VSS"],
)

# OR4: 4-input OR
or4_1 = logic_module(
    "sg13g2_or4_1",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "D", "VDD", "VSS"],
)
or4_2 = logic_module(
    "sg13g2_or4_2",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "C", "D", "VDD", "VSS"],
)

# NAND2: 2-input NAND
nand2_1 = logic_module(
    "sg13g2_nand2_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "VDD", "VSS"],
)
nand2_2 = logic_module(
    "sg13g2_nand2_2",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "VDD", "VSS"],
)

# NAND2B: 2-input NAND with one inverted input
nand2b_1 = logic_module(
    "sg13g2_nand2b_1",
    "SG13G2 Standard Cell",
    ["Y", "A_N", "B", "VDD", "VSS"],
)
nand2b_2 = logic_module(
    "sg13g2_nand2b_2",
    "SG13G2 Standard Cell",
    ["Y", "A_N", "B", "VDD", "VSS"],
)

# NAND3: 3-input NAND
nand3_1 = logic_module(
    "sg13g2_nand3_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "C", "VDD", "VSS"],
)

# NAND3B: 3-input NAND with one inverted input
nand3b_1 = logic_module(
    "sg13g2_nand3b_1",
    "SG13G2 Standard Cell",
    ["Y", "A_N", "B", "C", "VDD", "VSS"],
)

# NAND4: 4-input NAND
nand4_1 = logic_module(
    "sg13g2_nand4_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "C", "D", "VDD", "VSS"],
)

# NOR2: 2-input NOR
nor2_1 = logic_module(
    "sg13g2_nor2_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "VDD", "VSS"],
)
nor2_2 = logic_module(
    "sg13g2_nor2_2",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "VDD", "VSS"],
)

# NOR2B: 2-input NOR with one inverted input
nor2b_1 = logic_module(
    "sg13g2_nor2b_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B_N", "VDD", "VSS"],
)
nor2b_2 = logic_module(
    "sg13g2_nor2b_2",
    "SG13G2 Standard Cell",
    ["Y", "A", "B_N", "VDD", "VSS"],
)

# NOR3: 3-input NOR
nor3_1 = logic_module(
    "sg13g2_nor3_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "C", "VDD", "VSS"],
)
nor3_2 = logic_module(
    "sg13g2_nor3_2",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "C", "VDD", "VSS"],
)

# NOR4: 4-input NOR
nor4_1 = logic_module(
    "sg13g2_nor4_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "C", "D", "VDD", "VSS"],
)
nor4_2 = logic_module(
    "sg13g2_nor4_2",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "C", "D", "VDD", "VSS"],
)

# O21AI: OR-AND-Invert (A1 | A2) & B1, inverted
o21ai_1 = logic_module(
    "sg13g2_o21ai_1",
    "SG13G2 Standard Cell",
    ["Y", "A1", "A2", "B1", "VDD", "VSS"],
)

# XOR2: 2-input XOR
xor2_1 = logic_module(
    "sg13g2_xor2_1",
    "SG13G2 Standard Cell",
    ["X", "A", "B", "VDD", "VSS"],
)

# XNOR2: 2-input XNOR
xnor2_1 = logic_module(
    "sg13g2_xnor2_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "B", "VDD", "VSS"],
)

# ============================================================================
# Buffers and Inverters
# ============================================================================

# BUF: Non-inverting buffer
buf_1 = logic_module(
    "sg13g2_buf_1",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)
buf_2 = logic_module(
    "sg13g2_buf_2",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)
buf_4 = logic_module(
    "sg13g2_buf_4",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)
buf_8 = logic_module(
    "sg13g2_buf_8",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)
buf_16 = logic_module(
    "sg13g2_buf_16",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)

# INV: Inverter
inv_1 = logic_module(
    "sg13g2_inv_1",
    "SG13G2 Standard Cell",
    ["Y", "A", "VDD", "VSS"],
)
inv_2 = logic_module(
    "sg13g2_inv_2",
    "SG13G2 Standard Cell",
    ["Y", "A", "VDD", "VSS"],
)
inv_4 = logic_module(
    "sg13g2_inv_4",
    "SG13G2 Standard Cell",
    ["Y", "A", "VDD", "VSS"],
)
inv_8 = logic_module(
    "sg13g2_inv_8",
    "SG13G2 Standard Cell",
    ["Y", "A", "VDD", "VSS"],
)
inv_16 = logic_module(
    "sg13g2_inv_16",
    "SG13G2 Standard Cell",
    ["Y", "A", "VDD", "VSS"],
)

# ============================================================================
# Tri-state Buffers
# ============================================================================

# EBUFN: Tri-state buffer (active low enable)
ebufn_2 = logic_module(
    "sg13g2_ebufn_2",
    "SG13G2 Standard Cell",
    ["Z", "A", "TE_B", "VDD", "VSS"],
)
ebufn_4 = logic_module(
    "sg13g2_ebufn_4",
    "SG13G2 Standard Cell",
    ["Z", "A", "TE_B", "VDD", "VSS"],
)
ebufn_8 = logic_module(
    "sg13g2_ebufn_8",
    "SG13G2 Standard Cell",
    ["Z", "A", "TE_B", "VDD", "VSS"],
)

# EINVN: Tri-state inverter (active low enable)
einvn_2 = logic_module(
    "sg13g2_einvn_2",
    "SG13G2 Standard Cell",
    ["Z", "A", "TE_B", "VDD", "VSS"],
)
einvn_4 = logic_module(
    "sg13g2_einvn_4",
    "SG13G2 Standard Cell",
    ["Z", "A", "TE_B", "VDD", "VSS"],
)
einvn_8 = logic_module(
    "sg13g2_einvn_8",
    "SG13G2 Standard Cell",
    ["Z", "A", "TE_B", "VDD", "VSS"],
)

# ============================================================================
# Multiplexers
# ============================================================================

# MUX2: 2-to-1 multiplexer
mux2_1 = logic_module(
    "sg13g2_mux2_1",
    "SG13G2 Standard Cell",
    ["X", "A0", "A1", "S", "VDD", "VSS"],
)
mux2_2 = logic_module(
    "sg13g2_mux2_2",
    "SG13G2 Standard Cell",
    ["X", "A0", "A1", "S", "VDD", "VSS"],
)

# MUX4: 4-to-1 multiplexer
mux4_1 = logic_module(
    "sg13g2_mux4_1",
    "SG13G2 Standard Cell",
    ["X", "A0", "A1", "A2", "A3", "S0", "S1", "VDD", "VSS"],
)

# ============================================================================
# Sequential Logic - Flip-Flops
# ============================================================================

# DFRBP: D flip-flop with reset, both Q and Q_N outputs
dfrbp_1 = logic_module(
    "sg13g2_dfrbp_1",
    "SG13G2 Standard Cell",
    ["Q", "Q_N", "CLK", "D", "RESET_B", "VDD", "VSS"],
)
dfrbp_2 = logic_module(
    "sg13g2_dfrbp_2",
    "SG13G2 Standard Cell",
    ["Q", "Q_N", "CLK", "D", "RESET_B", "VDD", "VSS"],
)

# DFRBPQ: D flip-flop with reset, Q output only
dfrbpq_1 = logic_module(
    "sg13g2_dfrbpq_1",
    "SG13G2 Standard Cell",
    ["Q", "CLK", "D", "RESET_B", "VDD", "VSS"],
)
dfrbpq_2 = logic_module(
    "sg13g2_dfrbpq_2",
    "SG13G2 Standard Cell",
    ["Q", "CLK", "D", "RESET_B", "VDD", "VSS"],
)

# SDFRBP: Scan D flip-flop with reset, both Q and Q_N outputs
sdfrbp_1 = logic_module(
    "sg13g2_sdfrbp_1",
    "SG13G2 Standard Cell",
    ["Q", "Q_N", "CLK", "D", "RESET_B", "SCD", "SCE", "VDD", "VSS"],
)
sdfrbp_2 = logic_module(
    "sg13g2_sdfrbp_2",
    "SG13G2 Standard Cell",
    ["Q", "Q_N", "CLK", "D", "RESET_B", "SCD", "SCE", "VDD", "VSS"],
)

# SDFRBPQ: Scan D flip-flop with reset, Q output only
sdfrbpq_1 = logic_module(
    "sg13g2_sdfrbpq_1",
    "SG13G2 Standard Cell",
    ["Q", "CLK", "D", "RESET_B", "SCD", "SCE", "VDD", "VSS"],
)
sdfrbpq_2 = logic_module(
    "sg13g2_sdfrbpq_2",
    "SG13G2 Standard Cell",
    ["Q", "CLK", "D", "RESET_B", "SCD", "SCE", "VDD", "VSS"],
)

# SDFBBP: Scan D flip-flop with reset and set, both Q and Q_N outputs
sdfbbp_1 = logic_module(
    "sg13g2_sdfbbp_1",
    "SG13G2 Standard Cell",
    ["Q", "Q_N", "CLK", "D", "RESET_B", "SCD", "SCE", "SET_B", "VDD", "VSS"],
)

# ============================================================================
# Sequential Logic - Latches
# ============================================================================

# DLHQ: D latch (high-level transparent), Q output only
dlhq_1 = logic_module(
    "sg13g2_dlhq_1",
    "SG13G2 Standard Cell",
    ["Q", "D", "GATE", "VDD", "VSS"],
)

# DLHR: D latch (high-level transparent) with reset, both Q and Q_N outputs
dlhr_1 = logic_module(
    "sg13g2_dlhr_1",
    "SG13G2 Standard Cell",
    ["Q", "Q_N", "D", "GATE", "RESET_B", "VDD", "VSS"],
)

# DLHRQ: D latch (high-level transparent) with reset, Q output only
dlhrq_1 = logic_module(
    "sg13g2_dlhrq_1",
    "SG13G2 Standard Cell",
    ["Q", "D", "GATE", "RESET_B", "VDD", "VSS"],
)

# DLLR: D latch (low-level transparent) with reset, both Q and Q_N outputs
dllr_1 = logic_module(
    "sg13g2_dllr_1",
    "SG13G2 Standard Cell",
    ["Q", "Q_N", "D", "GATE_N", "RESET_B", "VDD", "VSS"],
)

# DLLRQ: D latch (low-level transparent) with reset, Q output only
dllrq_1 = logic_module(
    "sg13g2_dllrq_1",
    "SG13G2 Standard Cell",
    ["Q", "D", "GATE_N", "RESET_B", "VDD", "VSS"],
)

# ============================================================================
# Clock Gating Cells
# ============================================================================

# LGCP: Latch-based clock gating cell
lgcp_1 = logic_module(
    "sg13g2_lgcp_1",
    "SG13G2 Standard Cell",
    ["GCLK", "CLK", "GATE", "VDD", "VSS"],
)

# SLGCP: Scan latch-based clock gating cell
slgcp_1 = logic_module(
    "sg13g2_slgcp_1",
    "SG13G2 Standard Cell",
    ["GCLK", "CLK", "GATE", "SCE", "VDD", "VSS"],
)

# ============================================================================
# Delay Cells
# ============================================================================

# DLYGATE4SD: 4-stage delay cell (different flavors)
dlygate4sd1_1 = logic_module(
    "sg13g2_dlygate4sd1_1",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)
dlygate4sd2_1 = logic_module(
    "sg13g2_dlygate4sd2_1",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)
dlygate4sd3_1 = logic_module(
    "sg13g2_dlygate4sd3_1",
    "SG13G2 Standard Cell",
    ["X", "A", "VDD", "VSS"],
)

# ============================================================================
# Special Cells
# ============================================================================

# TIEHI: Tie high cell
tiehi = logic_module(
    "sg13g2_tiehi",
    "SG13G2 Standard Cell",
    ["L_HI", "VDD", "VSS"],
)

# TIELO: Tie low cell
tielo = logic_module(
    "sg13g2_tielo",
    "SG13G2 Standard Cell",
    ["L_LO", "VDD", "VSS"],
)

# ANTENNANP: Antenna cell
antennanp = logic_module(
    "sg13g2_antennanp",
    "SG13G2 Standard Cell",
    ["A", "VDD", "VSS"],
)

# SIGHOLD: Signal hold cell
sighold = logic_module(
    "sg13g2_sighold",
    "SG13G2 Standard Cell",
    ["SH", "VDD", "VSS"],
)

# ============================================================================
# Filler Cells
# ============================================================================

# FILL: Filler cells for unused space
fill_1 = logic_module(
    "sg13g2_fill_1",
    "SG13G2 Standard Cell",
    ["VDD", "VSS"],
)
fill_2 = logic_module(
    "sg13g2_fill_2",
    "SG13G2 Standard Cell",
    ["VDD", "VSS"],
)
fill_4 = logic_module(
    "sg13g2_fill_4",
    "SG13G2 Standard Cell",
    ["VDD", "VSS"],
)
fill_8 = logic_module(
    "sg13g2_fill_8",
    "SG13G2 Standard Cell",
    ["VDD", "VSS"],
)

# DECAP: Decoupling capacitor cells
decap_4 = logic_module(
    "sg13g2_decap_4",
    "SG13G2 Standard Cell",
    ["VDD", "VSS"],
)
decap_8 = logic_module(
    "sg13g2_decap_8",
    "SG13G2 Standard Cell",
    ["VDD", "VSS"],
)
