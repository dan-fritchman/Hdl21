"""
# Test Content

A semi-comprehensive set of Hdl21 features, for use in testing related packages, e.g. PDKs. 
"""

import hdl21 as h


@h.bundle
class Abc:
    a, b, c = h.Ports(3)


@h.paramclass
class N:
    n = h.Param(dtype=int, desc="n")


@h.module
class Bot:
    abc = Abc(port=True)
    a, b, c = h.Ports(3, width=2)


@h.generator
def Inner(params: N) -> h.Module:
    Empty = h.Module(name="Empty")
    EmptyEmod = h.ExternalModule(name="EmptyEmod", port_list=[])

    @h.module
    class Inner:
        abc = Abc()
        a, b, c = h.Signals(3, width=2)
        bot = Bot(abc=abc, a=a, b=b, c=h.Concat(c[1], c[0]))
        emod_call = EmptyEmod()()
        empty_array = params.n * Empty()

    return Inner


@h.generator
def Top1(_: N) -> h.Module:
    m = h.Module()
    m.i = Inner(n=5)()
    return m


@h.module
class Top2:
    i = Inner(n=5)


def walker_test_content():
    """Create a set of content for a `h.HierarchyWalker` test.
    Returns a list of combinations of modules, generator calls, and all the internal features inside."""
    return [Top1(N(1)), Top2]
