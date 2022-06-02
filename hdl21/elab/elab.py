"""
# Elaboration 

Defines the primary `elaborate` method used to flesh out an in-memory `Module` or `Generator`. 
Internally defines and uses a number of hierarchical visitor-classes which traverse the hardware hierarchy, 
performing one or more transformation-passes.  
"""

# Std-Lib Imports
from types import SimpleNamespace
from typing import Any, List, Optional

# Local imports
from ..module import Module
from .elaboratable import Elabable, Elabables, is_elabable
from .context import Context
from .elabpass import ElabPass


def elab_all(top: Elabables, **kwargs) -> List[Elabable]:
    """ Elaborate everything we can find - potentially recursively - in `Elabables` `top`. 

    Results are returned in a list, not necessarily reproducing the structure of `top`. 
    Note the *attributes* of `top` are also generally modified in-place, allowing access to their elaboration results. """
    # Recursively create a list of all elab-able types in `obj`
    ls = []
    _list_elabables_helper(top, ls)
    # Elaborate each, and return them as a list
    return [elaborate(top=t, **kwargs) for t in ls]


def _list_elabables_helper(obj: Any, accum: list) -> None:
    """ Recursive helper for hierarchically finding elaborate-able things in `obj`. 
    Newly-found items are appended to accumulation-list `accum`. """
    if is_elabable(obj):
        accum.append(obj)
    elif isinstance(obj, list):
        [_list_elabables_helper(i, accum) for i in obj]
    elif isinstance(obj, SimpleNamespace):
        # Note this skips over non-elaboratable items (e.g. names), where the list demands all be suitable.
        for i in obj.__dict__.values():
            if isinstance(i, (SimpleNamespace, list)) or is_elabable(i):
                _list_elabables_helper(i, accum)
    else:
        raise TypeError(f"Attempting Invalid Elaboration of {obj}")


def elaborate(
    top: Elabable,
    *,
    ctx: Optional[Context] = None,
    passes: Optional[List[ElabPass]] = None,
) -> Module:
    """ In-Memory Elaboration of Generator or Module `top`. 
    
    Optional `passes` lists the ordered `ElabPass`es to run. By default it runs the order specified by `ElabPass.default`. 
    Note the order of passes is important; many depend upon others to have completed before they can successfully run. 

    Optional `Context` field `ctx` is not yet supported. 

    `elaborate` executes elaboration of a *single* `top` object. 
    For (plural) combinations of `Elabable` objects, use `elab_all`. 
    """
    # Expand default values
    ctx = ctx or Context()
    passes = passes or ElabPass.default()

    # Pass `top` through each of our passes, in order
    res = top
    for pass_ in passes:
        res = pass_.value.elaborate(top=res, ctx=ctx)
    return res
