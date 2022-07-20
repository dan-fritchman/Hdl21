"""
# Elaboration 

Defines the primary `elaborate` method used to flesh out an in-memory `Module` or `Generator`. 
Internally defines and uses a number of hierarchical visitor-classes which traverse the hardware hierarchy, 
performing one or more transformation-passes.  
"""

# Std-Lib Imports
from typing import List, Optional

# Local imports
from .elaboratable import Elaboratable, Elaboratables
from .context import Context
from .elabpass import ElabPass


def elaborate(
    top: Elaboratables,
    *,
    ctx: Optional[Context] = None,
    passes: Optional[List[ElabPass]] = None,
) -> Elaboratables:
    """
    # Hdl21 Elaboration

    In-memory elaborates of `Module`s, calls to `Generator`s, and lists thereof.

    Optional `passes` lists the ordered `ElabPass`es to run. By default it runs the order specified by `ElabPass.default`.
    Note the order of passes is important; many depend upon others to have completed before they can successfully run.

    Optional `Context` field `ctx` is not yet supported.
    """

    # Expand default values
    ctx = ctx or Context()
    passes = passes or ElabPass.default()

    # Check whether we are elaborating a single object or a list thereof
    tops = top if isinstance(top, List) else [top]

    def run_passes(t: Elaboratable):
        # Pass `t` through each of our passes, in order
        for elabpass in passes:
            t = elabpass.elaborate(top=t, ctx=ctx)
        return t

    # Pass each of our top-level objects through the passes
    rv = list(map(run_passes, tops))

    # Extract the single-element case
    if not isinstance(top, List):
        return rv[0]
    return rv
