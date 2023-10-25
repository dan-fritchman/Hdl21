""" 
# Hdl21 Built-In Generators 
# Unit Tests 
"""

import hdl21 as h
from hdl21.generator import GeneratorCall


def test_mos_generator():
    """Initial test of built-in series-Mos generator"""

    Mos = h.generators.MosStack
    m = Mos(Mos.Params(nser=2))
    call = m._generated_by

    assert isinstance(call, GeneratorCall)
    assert isinstance(call.params, Mos.Params)

    m = h.elaborate(m)

    assert isinstance(m, h.Module)
    assert len(m.ports) == 4
    assert m.ports.keys() == h.primitives.Mos.ports.keys()
    assert len(m.instances) == 2
    assert "units_0" in m.instances
    assert "units_1" in m.instances
    assert isinstance(m.instances["units_0"].of, h.PrimitiveCall)
    assert isinstance(m.instances["units_1"].of, h.PrimitiveCall)
    assert m.instances["units_0"].of.params == h.primitives.MosParams()
    assert m.instances["units_1"].of.params == h.primitives.MosParams()

    assert len(m.signals) == 1
    assert "i" in m.signals


def test_series_generator():
    """# Test `h.generators.Series`"""

    from hdl21.generators import Series

    @h.module
    class M:  # Unit cell
        a, b, c, d, e, f, g = h.Ports(7)

    params = Series.Params(unit=M, nser=2, conns=["a", "b"])
    m = Series(params)
    call = m._generated_by

    assert isinstance(call, GeneratorCall)
    assert isinstance(call.params, Series.Params)

    m = h.elaborate(m)

    assert isinstance(m, h.Module)
    assert len(m.ports) == 7
    assert m.ports.keys() == M.ports.keys()
    assert len(m.instances) == 2
    assert "units_0" in m.instances
    assert "units_1" in m.instances

    assert len(m.signals) == 1
    assert "i" in m.signals

    for inst in m.instances.values():
        assert inst.of is M
