import importlib
from pathlib import Path
from types import FrameType, ModuleType
from hdl21.source_info import source_info, SourceInfo


def test_source_info():
    """Test getting `SourceInfo` for the current call-stack.
    Note the `linenum` assertions here generally change if this file changes.
    This file is kept short on purpose!"""

    call = source_info(get_pymodule=True)

    assert isinstance(call, SourceInfo)
    assert call.filepath == Path(__file__)
    assert call.linenum == 12
    assert isinstance(call.pymodule, ModuleType)

    call = source_info(get_pymodule=False)

    assert isinstance(call, SourceInfo)
    assert call.filepath == Path(__file__)
    assert call.linenum == 19
    assert call.pymodule is None
