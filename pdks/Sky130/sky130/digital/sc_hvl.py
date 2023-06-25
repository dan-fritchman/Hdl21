import hdl21 as h
from typing import Dict
from ..pdk_data import _logic_module
from types import SimpleNamespace

hvl: Dict[str, h.ExternalModule] = {
    "a21o_1": _logic_module(
        "a21o_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a21oi_1": _logic_module(
        "a21oi_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a22o_1": _logic_module(
        "a22o_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a22oi_1": _logic_module(
        "a22oi_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "and2_1": _logic_module(
        "and2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and3_1": _logic_module(
        "and3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_1": _logic_module(
        "buf_1",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_2": _logic_module(
        "buf_2",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_4": _logic_module(
        "buf_4",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_8": _logic_module(
        "buf_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_16": _logic_module(
        "buf_16",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_32": _logic_module(
        "buf_32",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "conb_1": _logic_module(
        "conb_1",
        "High Voltage",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "decap_4": _logic_module(
        "decap_4", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "decap_8": _logic_module(
        "decap_8", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "dfrbp_1": _logic_module(
        "dfrbp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfrtp_1": _logic_module(
        "dfrtp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfsbp_1": _logic_module(
        "dfsbp_1",
        "High Voltage",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfstp_1": _logic_module(
        "dfstp_1",
        "High Voltage",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfxbp_1": _logic_module(
        "dfxbp_1",
        "High Voltage",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfxtp_1": _logic_module(
        "dfxtp_1",
        "High Voltage",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "diode_2": _logic_module(
        "diode_2",
        "High Voltage",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "dlclkp_1": _logic_module(
        "dlclkp_1",
        "High Voltage",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "dlrtp_1": _logic_module(
        "dlrtp_1",
        "High Voltage",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlxtp_1": _logic_module(
        "dlxtp_1",
        "High Voltage",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "einvn_1": _logic_module(
        "einvn_1",
        "High Voltage",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvp_1": _logic_module(
        "einvp_1",
        "High Voltage",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "fill_1": _logic_module(
        "fill_1", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "fill_2": _logic_module(
        "fill_2", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "fill_4": _logic_module(
        "fill_4", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "fill_8": _logic_module(
        "fill_8", "High Voltage", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "inv_1": _logic_module(
        "inv_1",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_2": _logic_module(
        "inv_2",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_4": _logic_module(
        "inv_4",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_8": _logic_module(
        "inv_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_16": _logic_module(
        "inv_16",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "lsbufhv2hv_hl_1": _logic_module(
        "lsbufhv2hv_hl_1",
        "High Voltage",
        ["A", "LOWHVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "lsbufhv2hv_lh_1": _logic_module(
        "lsbufhv2hv_lh_1",
        "High Voltage",
        ["A", "LOWHVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "lsbufhv2lv_1": _logic_module(
        "lsbufhv2lv_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "lsbufhv2lv_simple_1": _logic_module(
        "lsbufhv2lv_simple_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "lsbuflv2hv_1": _logic_module(
        "lsbuflv2hv_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "lsbuflv2hv_clkiso_hlkg_3": _logic_module(
        "lsbuflv2hv_clkiso_hlkg_3",
        "High Voltage",
        ["A", "SLEEP_B", "LVPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "lsbuflv2hv_isosrchvaon_1": _logic_module(
        "lsbuflv2hv_isosrchvaon_1",
        "High Voltage",
        ["A", "SLEEP_B", "LVPWR", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "lsbuflv2hv_symmetric_1": _logic_module(
        "lsbuflv2hv_symmetric_1",
        "High Voltage",
        ["A", "LVPWR", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux2_1": _logic_module(
        "mux2_1",
        "High Voltage",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux4_1": _logic_module(
        "mux4_1",
        "High Voltage",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "nand2_1": _logic_module(
        "nand2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand3_1": _logic_module(
        "nand3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2_1": _logic_module(
        "nor2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor3_1": _logic_module(
        "nor3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o21a_1": _logic_module(
        "o21a_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o21ai_1": _logic_module(
        "o21ai_1",
        "High Voltage",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o22a_1": _logic_module(
        "o22a_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o22ai_1": _logic_module(
        "o22ai_1",
        "High Voltage",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "or2_1": _logic_module(
        "or2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or3_1": _logic_module(
        "or3_1",
        "High Voltage",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "probe_p_8": _logic_module(
        "probe_p_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "probec_p_8": _logic_module(
        "probec_p_8",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "schmittbuf_1": _logic_module(
        "schmittbuf_1",
        "High Voltage",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sdfrbp_1": _logic_module(
        "sdfrbp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfrtp_1": _logic_module(
        "sdfrtp_1",
        "High Voltage",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfsbp_1": _logic_module(
        "sdfsbp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfstp_1": _logic_module(
        "sdfstp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfxbp_1": _logic_module(
        "sdfxbp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfxtp_1": _logic_module(
        "sdfxtp_1",
        "High Voltage",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdlclkp_1": _logic_module(
        "sdlclkp_1",
        "High Voltage",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sdlxtp_1": _logic_module(
        "sdlxtp_1",
        "High Voltage",
        ["D", "GATE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "xnor2_1": _logic_module(
        "xnor2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "xor2_1": _logic_module(
        "xor2_1",
        "High Voltage",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

# Collected `ExternalModule`s are stored in the `modules` namespace
high_voltage = SimpleNamespace()

for name, mod in hvl.items():
    setattr(high_voltage, name, mod)
