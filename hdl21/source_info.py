"""
# Python Source Info

Track the source file and line number of user calls. 
"""

import inspect
from pathlib import Path 
from types import ModuleType
from typing import Optional, List  

from pydantic.dataclasses import dataclass


@dataclass 
class SourceInfo:
    filepath: Path 
    linenum: int
    pymodule: Optional[ModuleType]


def source_info(skipfiles: List[str]) -> Optional[SourceInfo]:
    """ 
    # Get Source Info

    Find the (python) source of the first python-stack-frame from outside `skipfiles` (plus *this* file). 
    Returns `None` if *no* such modules are in the call-stack. 
    """

    if not isinstance(skipfiles, list):
        raise RuntimeError("Internal Error - source_info() called with non-list skipfiles")

    skipfiles = set(skipfiles)
    skipfiles.add(__file__)

    for frame in inspect.stack():
        if frame.filename not in skipfiles:
            # Note frames produce an `Optional[ModuleType]`.
            # (It seems extension modules may not have one.)
            pymodule = inspect.getmodule(frame[0])
            return SourceInfo(filepath=Path(frame.filename), linenum=frame.lineno, pymodule=pymodule)

    # No caller outside `skipfiles` found anywhere in the call-stack.
    return None
