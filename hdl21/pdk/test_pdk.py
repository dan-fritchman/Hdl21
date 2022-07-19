from .corner import Corner, CornerType, CmosCorner


def test_corner1():
    assert str(Corner.TYP) == "Corner.TYP"
    assert str(Corner.FAST) == "Corner.FAST"
    assert str(Corner.SLOW) == "Corner.SLOW"


def test_cornertype1():
    assert str(CornerType.MOS) == "CornerType.MOS"
    assert str(CornerType.CMOS) == "CornerType.CMOS"
    assert str(CornerType.RES) == "CornerType.RES"
    assert str(CornerType.CAP) == "CornerType.CAP"


def test_cmos1():
    assert str(CmosCorner.TT) == "CmosCorner.TT"
    assert str(CmosCorner.FF) == "CmosCorner.FF"
    assert str(CmosCorner.SS) == "CmosCorner.SS"
    assert str(CmosCorner.FS) == "CmosCorner.FS"
    assert str(CmosCorner.SF) == "CmosCorner.SF"
