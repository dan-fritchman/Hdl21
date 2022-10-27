"""
# Python Source Info

Track the source file and line number of user calls. 

This source-level tracking is invaluable for hierarchical hardware designs, 
especially since the Hdl21 elaboration process means default debugger errors 
do not produce a stack-trace through the *hardware*, but through the *elaborators*. 

Most of the logic to produce nice error messages using `SourceInfo`s 
is in `Elaborator`s, particularly the base-class `Elaborator`'s `fail` method. 

The mechanisms for tracking this source info have been the subject of some experimentation. 
Past methods, and associated lessons include: 

* `inspect.stack()` and `inspect.getmodule()` are REALLY slow. 
  * Versions of Hdl21 overusing these methods have observed them taking as much as 90% of elaboration time. 
  * `stack()` in particular does not abide the Python3 "everything is a generator" rule, and computes all stack-frames into a list upfront
  * We still use `getmodule()` as a basis for (Hdl21) Module naming. But beware to limit its calls, and get rid of it if we can. 
* Storing the `frame` object returned by `inspect.currentframe()` at creation time and referring back to it later, just doesn't work. 
  * The `frame` objects are mutated directly by the interpreter; the stack is lost essentially immediately. 

"""

import inspect
from pathlib import Path
from types import ModuleType, FrameType
from typing import Optional, Set

from pydantic.dataclasses import dataclass


@dataclass
class SourceInfo:
    """# Python Source Info"""

    filepath: Path
    linenum: int
    pymodule: Optional[ModuleType] = None


def source_info(get_pymodule: bool = False) -> Optional[SourceInfo]:
    """
    # Get Source Info

    Find the source details of the first python-stack-frame from outside `files_to_skip`.
    Returns `None` if *no* such modules are in the call-stack.

    Returns a `SourceInfo` with `filepath` and `linenum` fields,
    and additionally finds the `pymodule` python module field if requested
    via the `get_pymodule` boolean argument.
    """

    # Get or create the files-to-skip set
    global files_to_skip
    if files_to_skip is None:
        files_to_skip = get_files_to_skip()
    # Note: this file is in the `files_to_skip` list, so this function's call-stack entry will never show up.

    frame: Optional[FrameType] = inspect.currentframe()
    MAX_DEPTH = 1000  # Avoid infinite recursion

    for _ in range(MAX_DEPTH):
        if frame is None:
            return None
        if frame.f_code.co_filename not in files_to_skip:
            # We've got a hit! Return a `SourceInfo` object.

            # If requested via the `get_pymodule` flag, return the Python module.
            # Note this is generally the slow part.
            pymodule = None if not get_pymodule else inspect.getmodule(frame)

            return SourceInfo(
                filepath=Path(frame.f_code.co_filename),
                linenum=frame.f_lineno,
                pymodule=pymodule,
            )
        # And back up one frame
        frame = frame.f_back

    # If we got here without returning, we failed.
    raise RecursionError("Error finding `SourceDetail`")


# Set of files to skip
# Calculated once, after import-time, so those modules can import this one.
# files_to_skip: Optional[Set[str]] = None
files_to_skip = None


def get_files_to_skip():
    """Create the list of files to skip.
    Should only be run once, shortly after import-time."""

    from . import (
        _module_module,
        _external_module_module,
        _generator_module,
        _instance_module,
    )

    return set(
        [
            __file__,  # *This* file
            _module_module.__file__,
            _external_module_module.__file__,
            _generator_module.__file__,
            _instance_module.__file__,
        ]
    )
