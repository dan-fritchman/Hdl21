"""
# `Diff` Differential Bundle and `Pair` Instance Pair 
"""

# Std-Lib Imports
from enum import Enum, auto

# Local imports
from .signal import Signals
from .instance import InstanceBundleType
from .bundle import bundle, AnonymousBundle


@bundle
class Diff:
    """Differential Bundle"""

    class Roles(Enum):
        SOURCE = auto()
        SINK = auto()

    p, n = Signals(2, src=Roles.SOURCE, dest=Roles.SINK)


def inverse(d: Diff) -> AnonymousBundle:
    """Create a Bundle with the same signals as `d`, but with `p` and `n` reversed."""
    return AnonymousBundle(p=d.n, n=d.p)


# Instance Pair Class
Pair = InstanceBundleType(
    name="Pair",
    bundle=Diff,
    doc=f"""
        # Differential Instance Pair 

        Two identical instances of the same `Module` which can be connected to either `Diff` signal bundles or scalar `Signal`s.  
        The rules for connecting to the ports of `Pair`s are: 

        * When connecting to a `Diff`, the `p` and `n` signals are connected to the `p` and `n` instances, respectively. 
        * When connecting to a `Signal`, the `p` and `n` instances are connected in parallel to that signal. 
        * All other connections are disallowed. 

        Example: 
    
        ```python 
        import hdl21 as h

        @h.module 
        class DiffResistors:
            # Two identical, differential resistors to VSS
            VSS = h.Port()
            diff = h.Diff()
            # The `Pair` instance
            rs = h.Pair(MyResistor)(p=diff, n=VSS)
        ```
    """,
)


__all__ = ["Diff", "inverse", "Pair"]
