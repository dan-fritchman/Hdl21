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
    """ Differential Bundle """

    class Roles(Enum):
        SOURCE = auto()
        SINK = auto()

    p, n = Signals(2, src=Roles.SOURCE, dest=Roles.SINK)


def inverse(d: Diff) -> AnonymousBundle:
    """ Create a Bundle with the same signals as `d`, but with `p` and `n` reversed. """
    return AnonymousBundle(p=d.n, n=d.p)


Pair = InstanceBundleType(name="Pair", bundle=Diff)


__all__ = ["Diff", "inverse", "Pair"]
