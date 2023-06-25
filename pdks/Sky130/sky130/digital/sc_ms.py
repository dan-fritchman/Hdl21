import hdl21 as h
from typing import Dict
from ..pdk_data import _logic_module
from types import SimpleNamespace

ms: Dict[str, h.ExternalModule] = {
    "a2bb2o_1": _logic_module(
        "a2bb2o_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a2bb2o_2": _logic_module(
        "a2bb2o_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a2bb2o_4": _logic_module(
        "a2bb2o_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a2bb2oi_1": _logic_module(
        "a2bb2oi_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a2bb2oi_2": _logic_module(
        "a2bb2oi_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a2bb2oi_4": _logic_module(
        "a2bb2oi_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a21bo_1": _logic_module(
        "a21bo_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a21bo_2": _logic_module(
        "a21bo_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a21bo_4": _logic_module(
        "a21bo_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a21boi_1": _logic_module(
        "a21boi_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a21boi_2": _logic_module(
        "a21boi_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a21boi_4": _logic_module(
        "a21boi_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a21o_1": _logic_module(
        "a21o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a21o_2": _logic_module(
        "a21o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a21o_4": _logic_module(
        "a21o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a21oi_1": _logic_module(
        "a21oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a21oi_2": _logic_module(
        "a21oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a21oi_4": _logic_module(
        "a21oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a22o_1": _logic_module(
        "a22o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a22o_2": _logic_module(
        "a22o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a22o_4": _logic_module(
        "a22o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a22oi_1": _logic_module(
        "a22oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a22oi_2": _logic_module(
        "a22oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a22oi_4": _logic_module(
        "a22oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a31o_1": _logic_module(
        "a31o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a31o_2": _logic_module(
        "a31o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a31o_4": _logic_module(
        "a31o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a31oi_1": _logic_module(
        "a31oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a31oi_2": _logic_module(
        "a31oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a31oi_4": _logic_module(
        "a31oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a32o_1": _logic_module(
        "a32o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a32o_2": _logic_module(
        "a32o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a32o_4": _logic_module(
        "a32o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a32oi_1": _logic_module(
        "a32oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a32oi_2": _logic_module(
        "a32oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a32oi_4": _logic_module(
        "a32oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a41o_1": _logic_module(
        "a41o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a41o_2": _logic_module(
        "a41o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a41o_4": _logic_module(
        "a41o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a41oi_1": _logic_module(
        "a41oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a41oi_2": _logic_module(
        "a41oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a41oi_4": _logic_module(
        "a41oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a211o_1": _logic_module(
        "a211o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a211o_2": _logic_module(
        "a211o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a211o_4": _logic_module(
        "a211o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a211oi_1": _logic_module(
        "a211oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a211oi_2": _logic_module(
        "a211oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a211oi_4": _logic_module(
        "a211oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a221o_1": _logic_module(
        "a221o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a221o_2": _logic_module(
        "a221o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a221o_4": _logic_module(
        "a221o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a221oi_1": _logic_module(
        "a221oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a221oi_2": _logic_module(
        "a221oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a221oi_4": _logic_module(
        "a221oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a222o_1": _logic_module(
        "a222o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a222o_2": _logic_module(
        "a222o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a222oi_1": _logic_module(
        "a222oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a222oi_2": _logic_module(
        "a222oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "C2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a311o_1": _logic_module(
        "a311o_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a311o_2": _logic_module(
        "a311o_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a311o_4": _logic_module(
        "a311o_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a311oi_1": _logic_module(
        "a311oi_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a311oi_2": _logic_module(
        "a311oi_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a311oi_4": _logic_module(
        "a311oi_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a2111o_1": _logic_module(
        "a2111o_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a2111o_2": _logic_module(
        "a2111o_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a2111o_4": _logic_module(
        "a2111o_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "a2111oi_1": _logic_module(
        "a2111oi_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a2111oi_2": _logic_module(
        "a2111oi_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "a2111oi_4": _logic_module(
        "a2111oi_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "and2_1": _logic_module(
        "and2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and2_2": _logic_module(
        "and2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and2_4": _logic_module(
        "and2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and2b_1": _logic_module(
        "and2b_1",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and2b_2": _logic_module(
        "and2b_2",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and2b_4": _logic_module(
        "and2b_4",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and3_1": _logic_module(
        "and3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and3_2": _logic_module(
        "and3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and3_4": _logic_module(
        "and3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and3b_1": _logic_module(
        "and3b_1",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and3b_2": _logic_module(
        "and3b_2",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and3b_4": _logic_module(
        "and3b_4",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4_1": _logic_module(
        "and4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4_2": _logic_module(
        "and4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4_4": _logic_module(
        "and4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4b_1": _logic_module(
        "and4b_1",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4b_2": _logic_module(
        "and4b_2",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4b_4": _logic_module(
        "and4b_4",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4bb_1": _logic_module(
        "and4bb_1",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4bb_2": _logic_module(
        "and4bb_2",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "and4bb_4": _logic_module(
        "and4bb_4",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_1": _logic_module(
        "buf_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_2": _logic_module(
        "buf_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_4": _logic_module(
        "buf_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_8": _logic_module(
        "buf_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "buf_16": _logic_module(
        "buf_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "bufbuf_8": _logic_module(
        "bufbuf_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "bufbuf_16": _logic_module(
        "bufbuf_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "bufinv_8": _logic_module(
        "bufinv_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "bufinv_16": _logic_module(
        "bufinv_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkbuf_1": _logic_module(
        "clkbuf_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "clkbuf_2": _logic_module(
        "clkbuf_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "clkbuf_4": _logic_module(
        "clkbuf_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "clkbuf_8": _logic_module(
        "clkbuf_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "clkbuf_16": _logic_module(
        "clkbuf_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "clkdlyinv3sd1_1": _logic_module(
        "clkdlyinv3sd1_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkdlyinv3sd2_1": _logic_module(
        "clkdlyinv3sd2_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkdlyinv3sd3_1": _logic_module(
        "clkdlyinv3sd3_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkdlyinv5sd1_1": _logic_module(
        "clkdlyinv5sd1_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkdlyinv5sd2_1": _logic_module(
        "clkdlyinv5sd2_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkdlyinv5sd3_1": _logic_module(
        "clkdlyinv5sd3_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkinv_1": _logic_module(
        "clkinv_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkinv_2": _logic_module(
        "clkinv_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkinv_4": _logic_module(
        "clkinv_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkinv_8": _logic_module(
        "clkinv_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "clkinv_16": _logic_module(
        "clkinv_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "conb_1": _logic_module(
        "conb_1",
        "Medium Speed",
        ["VGND", "VNB", "VPB", "VPWR", "HI", "LO"],
    ),
    "decap_4": _logic_module("decap_4", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "decap_8": _logic_module("decap_8", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "dfbbn_1": _logic_module(
        "dfbbn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfbbn_2": _logic_module(
        "dfbbn_2",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfbbp_1": _logic_module(
        "dfbbp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfrbp_1": _logic_module(
        "dfrbp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfrbp_2": _logic_module(
        "dfrbp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfrtn_1": _logic_module(
        "dfrtn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfrtp_1": _logic_module(
        "dfrtp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfrtp_2": _logic_module(
        "dfrtp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfrtp_4": _logic_module(
        "dfrtp_4",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfsbp_1": _logic_module(
        "dfsbp_1",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfsbp_2": _logic_module(
        "dfsbp_2",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfstp_1": _logic_module(
        "dfstp_1",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfstp_2": _logic_module(
        "dfstp_2",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfstp_4": _logic_module(
        "dfstp_4",
        "Medium Speed",
        ["CLK", "D", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfxbp_1": _logic_module(
        "dfxbp_1",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfxbp_2": _logic_module(
        "dfxbp_2",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dfxtp_1": _logic_module(
        "dfxtp_1",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfxtp_2": _logic_module(
        "dfxtp_2",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dfxtp_4": _logic_module(
        "dfxtp_4",
        "Medium Speed",
        ["CLK", "D", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "diode_2": _logic_module(
        "diode_2",
        "Medium Speed",
        ["DIODE", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "dlclkp_1": _logic_module(
        "dlclkp_1",
        "Medium Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "dlclkp_2": _logic_module(
        "dlclkp_2",
        "Medium Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "dlclkp_4": _logic_module(
        "dlclkp_4",
        "Medium Speed",
        ["CLK", "GATE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "dlrbn_1": _logic_module(
        "dlrbn_1",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dlrbn_2": _logic_module(
        "dlrbn_2",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dlrbp_1": _logic_module(
        "dlrbp_1",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dlrbp_2": _logic_module(
        "dlrbp_2",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dlrtn_1": _logic_module(
        "dlrtn_1",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlrtn_2": _logic_module(
        "dlrtn_2",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlrtn_4": _logic_module(
        "dlrtn_4",
        "Medium Speed",
        ["D", "GATE_N", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlrtp_1": _logic_module(
        "dlrtp_1",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlrtp_2": _logic_module(
        "dlrtp_2",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlrtp_4": _logic_module(
        "dlrtp_4",
        "Medium Speed",
        ["D", "GATE", "RESET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlxbn_1": _logic_module(
        "dlxbn_1",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dlxbn_2": _logic_module(
        "dlxbn_2",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dlxbp_1": _logic_module(
        "dlxbp_1",
        "Medium Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "dlxtn_1": _logic_module(
        "dlxtn_1",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlxtn_2": _logic_module(
        "dlxtn_2",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlxtn_4": _logic_module(
        "dlxtn_4",
        "Medium Speed",
        ["D", "GATE_N", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlxtp_1": _logic_module(
        "dlxtp_1",
        "Medium Speed",
        ["D", "GATE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "dlygate4sd1_1": _logic_module(
        "dlygate4sd1_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "dlygate4sd2_1": _logic_module(
        "dlygate4sd2_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "dlygate4sd3_1": _logic_module(
        "dlygate4sd3_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "dlymetal6s2s_1": _logic_module(
        "dlymetal6s2s_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "dlymetal6s4s_1": _logic_module(
        "dlymetal6s4s_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "dlymetal6s6s_1": _logic_module(
        "dlymetal6s6s_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "ebufn_1": _logic_module(
        "ebufn_1",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "ebufn_2": _logic_module(
        "ebufn_2",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "ebufn_4": _logic_module(
        "ebufn_4",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "ebufn_8": _logic_module(
        "ebufn_8",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "edfxbp_1": _logic_module(
        "edfxbp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "edfxtp_1": _logic_module(
        "edfxtp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "einvn_1": _logic_module(
        "einvn_1",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvn_2": _logic_module(
        "einvn_2",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvn_4": _logic_module(
        "einvn_4",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvn_8": _logic_module(
        "einvn_8",
        "Medium Speed",
        ["A", "TE_B", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvp_1": _logic_module(
        "einvp_1",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvp_2": _logic_module(
        "einvp_2",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvp_4": _logic_module(
        "einvp_4",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "einvp_8": _logic_module(
        "einvp_8",
        "Medium Speed",
        ["A", "TE", "VGND", "VNB", "VPB", "VPWR", "Z"],
    ),
    "fa_1": _logic_module(
        "fa_1",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "fa_2": _logic_module(
        "fa_2",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "fa_4": _logic_module(
        "fa_4",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "fah_1": _logic_module(
        "fah_1",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "fah_2": _logic_module(
        "fah_2",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "fah_4": _logic_module(
        "fah_4",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "fahcin_1": _logic_module(
        "fahcin_1",
        "Medium Speed",
        ["A", "B", "CIN", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "fahcon_1": _logic_module(
        "fahcon_1",
        "Medium Speed",
        ["A", "B", "CI", "VGND", "VNB", "VPB", "VPWR", "COUT_N", "SUM"],
    ),
    "fill_1": _logic_module("fill_1", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "fill_2": _logic_module("fill_2", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "fill_4": _logic_module("fill_4", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "fill_8": _logic_module("fill_8", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "fill_diode_2": _logic_module(
        "fill_diode_2", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "fill_diode_4": _logic_module(
        "fill_diode_4", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "fill_diode_8": _logic_module(
        "fill_diode_8", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]
    ),
    "ha_1": _logic_module(
        "ha_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "ha_2": _logic_module(
        "ha_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "ha_4": _logic_module(
        "ha_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "COUT", "SUM"],
    ),
    "inv_1": _logic_module(
        "inv_1",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_2": _logic_module(
        "inv_2",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_4": _logic_module(
        "inv_4",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_8": _logic_module(
        "inv_8",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "inv_16": _logic_module(
        "inv_16",
        "Medium Speed",
        ["A", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "latchupcell": _logic_module("latchupcell", "Medium Speed", ["VGND", "VPWR"]),
    "maj3_1": _logic_module(
        "maj3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "maj3_2": _logic_module(
        "maj3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "maj3_4": _logic_module(
        "maj3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux2_1": _logic_module(
        "mux2_1",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux2_2": _logic_module(
        "mux2_2",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux2_4": _logic_module(
        "mux2_4",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux2i_1": _logic_module(
        "mux2i_1",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "mux2i_2": _logic_module(
        "mux2i_2",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "mux2i_4": _logic_module(
        "mux2i_4",
        "Medium Speed",
        ["A0", "A1", "S", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "mux4_1": _logic_module(
        "mux4_1",
        "Medium Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux4_2": _logic_module(
        "mux4_2",
        "Medium Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "mux4_4": _logic_module(
        "mux4_4",
        "Medium Speed",
        ["A0", "A1", "A2", "A3", "S0", "S1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "nand2_1": _logic_module(
        "nand2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand2_2": _logic_module(
        "nand2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand2_4": _logic_module(
        "nand2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand2_8": _logic_module(
        "nand2_8",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand2b_1": _logic_module(
        "nand2b_1",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand2b_2": _logic_module(
        "nand2b_2",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand2b_4": _logic_module(
        "nand2b_4",
        "Medium Speed",
        ["A_N", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand3_1": _logic_module(
        "nand3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand3_2": _logic_module(
        "nand3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand3_4": _logic_module(
        "nand3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand3b_1": _logic_module(
        "nand3b_1",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand3b_2": _logic_module(
        "nand3b_2",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand3b_4": _logic_module(
        "nand3b_4",
        "Medium Speed",
        ["A_N", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4_1": _logic_module(
        "nand4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4_2": _logic_module(
        "nand4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4_4": _logic_module(
        "nand4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4b_1": _logic_module(
        "nand4b_1",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4b_2": _logic_module(
        "nand4b_2",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4b_4": _logic_module(
        "nand4b_4",
        "Medium Speed",
        ["A_N", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4bb_1": _logic_module(
        "nand4bb_1",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4bb_2": _logic_module(
        "nand4bb_2",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nand4bb_4": _logic_module(
        "nand4bb_4",
        "Medium Speed",
        ["A_N", "B_N", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2_1": _logic_module(
        "nor2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2_2": _logic_module(
        "nor2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2_4": _logic_module(
        "nor2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2_8": _logic_module(
        "nor2_8",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2b_1": _logic_module(
        "nor2b_1",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2b_2": _logic_module(
        "nor2b_2",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor2b_4": _logic_module(
        "nor2b_4",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor3_1": _logic_module(
        "nor3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor3_2": _logic_module(
        "nor3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor3_4": _logic_module(
        "nor3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor3b_1": _logic_module(
        "nor3b_1",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor3b_2": _logic_module(
        "nor3b_2",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor3b_4": _logic_module(
        "nor3b_4",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4_1": _logic_module(
        "nor4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4_2": _logic_module(
        "nor4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4_4": _logic_module(
        "nor4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4b_1": _logic_module(
        "nor4b_1",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4b_2": _logic_module(
        "nor4b_2",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4b_4": _logic_module(
        "nor4b_4",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4bb_1": _logic_module(
        "nor4bb_1",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4bb_2": _logic_module(
        "nor4bb_2",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "nor4bb_4": _logic_module(
        "nor4bb_4",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o2bb2a_1": _logic_module(
        "o2bb2a_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o2bb2a_2": _logic_module(
        "o2bb2a_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o2bb2a_4": _logic_module(
        "o2bb2a_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o2bb2ai_1": _logic_module(
        "o2bb2ai_1",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o2bb2ai_2": _logic_module(
        "o2bb2ai_2",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o2bb2ai_4": _logic_module(
        "o2bb2ai_4",
        "Medium Speed",
        ["A1_N", "A2_N", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o21a_1": _logic_module(
        "o21a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o21a_2": _logic_module(
        "o21a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o21a_4": _logic_module(
        "o21a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o21ai_1": _logic_module(
        "o21ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o21ai_2": _logic_module(
        "o21ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o21ai_4": _logic_module(
        "o21ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o21ba_1": _logic_module(
        "o21ba_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o21ba_2": _logic_module(
        "o21ba_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o21ba_4": _logic_module(
        "o21ba_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o21bai_1": _logic_module(
        "o21bai_1",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o21bai_2": _logic_module(
        "o21bai_2",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o21bai_4": _logic_module(
        "o21bai_4",
        "Medium Speed",
        ["A1", "A2", "B1_N", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o22a_1": _logic_module(
        "o22a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o22a_2": _logic_module(
        "o22a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o22a_4": _logic_module(
        "o22a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o22ai_1": _logic_module(
        "o22ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o22ai_2": _logic_module(
        "o22ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o22ai_4": _logic_module(
        "o22ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o31a_1": _logic_module(
        "o31a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o31a_2": _logic_module(
        "o31a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o31a_4": _logic_module(
        "o31a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o31ai_1": _logic_module(
        "o31ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o31ai_2": _logic_module(
        "o31ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o31ai_4": _logic_module(
        "o31ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o32a_1": _logic_module(
        "o32a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o32a_2": _logic_module(
        "o32a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o32a_4": _logic_module(
        "o32a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o32ai_1": _logic_module(
        "o32ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o32ai_2": _logic_module(
        "o32ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o32ai_4": _logic_module(
        "o32ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "B2", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o41a_1": _logic_module(
        "o41a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o41a_2": _logic_module(
        "o41a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o41a_4": _logic_module(
        "o41a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o41ai_1": _logic_module(
        "o41ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o41ai_2": _logic_module(
        "o41ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o41ai_4": _logic_module(
        "o41ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "A4", "B1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o211a_1": _logic_module(
        "o211a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o211a_2": _logic_module(
        "o211a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o211a_4": _logic_module(
        "o211a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o211ai_1": _logic_module(
        "o211ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o211ai_2": _logic_module(
        "o211ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o211ai_4": _logic_module(
        "o211ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o221a_1": _logic_module(
        "o221a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o221a_2": _logic_module(
        "o221a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o221a_4": _logic_module(
        "o221a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o221ai_1": _logic_module(
        "o221ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o221ai_2": _logic_module(
        "o221ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o221ai_4": _logic_module(
        "o221ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "B2", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o311a_1": _logic_module(
        "o311a_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o311a_2": _logic_module(
        "o311a_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o311a_4": _logic_module(
        "o311a_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o311ai_1": _logic_module(
        "o311ai_1",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o311ai_2": _logic_module(
        "o311ai_2",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o311ai_4": _logic_module(
        "o311ai_4",
        "Medium Speed",
        ["A1", "A2", "A3", "B1", "C1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o2111a_1": _logic_module(
        "o2111a_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o2111a_2": _logic_module(
        "o2111a_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o2111a_4": _logic_module(
        "o2111a_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "o2111ai_1": _logic_module(
        "o2111ai_1",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o2111ai_2": _logic_module(
        "o2111ai_2",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "o2111ai_4": _logic_module(
        "o2111ai_4",
        "Medium Speed",
        ["A1", "A2", "B1", "C1", "D1", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "or2_1": _logic_module(
        "or2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or2_2": _logic_module(
        "or2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or2_4": _logic_module(
        "or2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or2b_1": _logic_module(
        "or2b_1",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or2b_2": _logic_module(
        "or2b_2",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or2b_4": _logic_module(
        "or2b_4",
        "Medium Speed",
        ["A", "B_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or3_1": _logic_module(
        "or3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or3_2": _logic_module(
        "or3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or3_4": _logic_module(
        "or3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or3b_1": _logic_module(
        "or3b_1",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or3b_2": _logic_module(
        "or3b_2",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or3b_4": _logic_module(
        "or3b_4",
        "Medium Speed",
        ["A", "B", "C_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4_1": _logic_module(
        "or4_1",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4_2": _logic_module(
        "or4_2",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4_4": _logic_module(
        "or4_4",
        "Medium Speed",
        ["A", "B", "C", "D", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4b_1": _logic_module(
        "or4b_1",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4b_2": _logic_module(
        "or4b_2",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4b_4": _logic_module(
        "or4b_4",
        "Medium Speed",
        ["A", "B", "C", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4bb_1": _logic_module(
        "or4bb_1",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4bb_2": _logic_module(
        "or4bb_2",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "or4bb_4": _logic_module(
        "or4bb_4",
        "Medium Speed",
        ["A", "B", "C_N", "D_N", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "sdfbbn_1": _logic_module(
        "sdfbbn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sdfbbn_2": _logic_module(
        "sdfbbn_2",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR"],
    ),
    "sdfbbp_1": _logic_module(
        "sdfbbp_1",
        "Medium Speed",
        [
            "CLK",
            "D",
            "RESET_B",
            "SCD",
            "SCE",
            "SET_B",
            "VGND",
            "VNB",
            "VPB",
            "VPWR",
            "Q",
        ],
    ),
    "sdfrbp_1": _logic_module(
        "sdfrbp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfrbp_2": _logic_module(
        "sdfrbp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfrtn_1": _logic_module(
        "sdfrtn_1",
        "Medium Speed",
        ["CLK_N", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfrtp_1": _logic_module(
        "sdfrtp_1",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfrtp_2": _logic_module(
        "sdfrtp_2",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfrtp_4": _logic_module(
        "sdfrtp_4",
        "Medium Speed",
        ["CLK", "D", "RESET_B", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfsbp_1": _logic_module(
        "sdfsbp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfsbp_2": _logic_module(
        "sdfsbp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfstp_1": _logic_module(
        "sdfstp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfstp_2": _logic_module(
        "sdfstp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfstp_4": _logic_module(
        "sdfstp_4",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "SET_B", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfxbp_1": _logic_module(
        "sdfxbp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfxbp_2": _logic_module(
        "sdfxbp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sdfxtp_1": _logic_module(
        "sdfxtp_1",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfxtp_2": _logic_module(
        "sdfxtp_2",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdfxtp_4": _logic_module(
        "sdfxtp_4",
        "Medium Speed",
        ["CLK", "D", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sdlclkp_1": _logic_module(
        "sdlclkp_1",
        "Medium Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sdlclkp_2": _logic_module(
        "sdlclkp_2",
        "Medium Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sdlclkp_4": _logic_module(
        "sdlclkp_4",
        "Medium Speed",
        ["CLK", "GATE", "SCE", "VGND", "VNB", "VPB", "VPWR", "GCLK"],
    ),
    "sedfxbp_1": _logic_module(
        "sedfxbp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sedfxbp_2": _logic_module(
        "sedfxbp_2",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q", "Q_N"],
    ),
    "sedfxtp_1": _logic_module(
        "sedfxtp_1",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sedfxtp_2": _logic_module(
        "sedfxtp_2",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "sedfxtp_4": _logic_module(
        "sedfxtp_4",
        "Medium Speed",
        ["CLK", "D", "DE", "SCD", "SCE", "VGND", "VNB", "VPB", "VPWR", "Q"],
    ),
    "tap_1": _logic_module("tap_1", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "tap_2": _logic_module("tap_2", "Medium Speed", ["VGND", "VNB", "VPB", "VPWR"]),
    "tapmet1_2": _logic_module("tapmet1_2", "Medium Speed", ["VGND", "VPB", "VPWR"]),
    "tapvgnd2_1": _logic_module("tapvgnd2_1", "Medium Speed", ["VGND", "VPB", "VPWR"]),
    "tapvgnd_1": _logic_module("tapvgnd_1", "Medium Speed", ["VGND", "VPB", "VPWR"]),
    "tapvpwrvgnd_1": _logic_module("tapvpwrvgnd_1", "Medium Speed", ["VGND", "VPWR"]),
    "xnor2_1": _logic_module(
        "xnor2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "xnor2_2": _logic_module(
        "xnor2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "xnor2_4": _logic_module(
        "xnor2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "Y"],
    ),
    "xnor3_1": _logic_module(
        "xnor3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xnor3_2": _logic_module(
        "xnor3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xnor3_4": _logic_module(
        "xnor3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xor2_1": _logic_module(
        "xor2_1",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xor2_2": _logic_module(
        "xor2_2",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xor2_4": _logic_module(
        "xor2_4",
        "Medium Speed",
        ["A", "B", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xor3_1": _logic_module(
        "xor3_1",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xor3_2": _logic_module(
        "xor3_2",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
    "xor3_4": _logic_module(
        "xor3_4",
        "Medium Speed",
        ["A", "B", "C", "VGND", "VNB", "VPB", "VPWR", "X"],
    ),
}

# Collected `ExternalModule`s are stored in the `modules` namespace
medium_speed = SimpleNamespace()

for name, mod in ms.items():
    setattr(medium_speed, name, mod)
