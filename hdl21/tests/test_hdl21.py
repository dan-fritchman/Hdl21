import pytest
from dataclasses import dataclass


def test_health():
    """ Test the core library is "there". 
    Also check whether the module-system's version """
    from .. import health as health1
    from hdl21 import health as health2

    a = health1()
    assert a == "alive"

    if health1 is not health2:
        import warnings
        import hdl21

        warnings.warn(f"Module under test is not installed version {hdl21}")


def test_module1():
    """ Initial Module Test """
    import hdl21 as h

    class M1(h.Module):
        a = h.Input()
        b = h.Output()
        c = h.Inout()
        d = h.Port()
        e = h.Signal()

    assert isinstance(M1, h.Module)
    assert isinstance(M1.ports, dict)
    assert isinstance(M1.signals, dict)
    assert isinstance(M1.instances, dict)
    assert "a" in M1.ports
    assert "a" not in M1.signals
    assert "b" in M1.ports
    assert "b" not in M1.signals
    assert "c" in M1.ports
    assert "c" not in M1.signals
    assert "d" in M1.ports
    assert "d" not in M1.signals
    assert "e" in M1.signals
    assert "e" not in M1.ports


def test_module2():
    import hdl21 as h

    class M1(h.Module):
        s = h.Input()

    class M2(h.Module):
        i = h.Instance(M1, s=q)
        q = h.Signal()

    assert isinstance(M1, h.Module)
    assert isinstance(M2, h.Module)
    assert isinstance(M1.ports["s"], h.Signal)
    assert isinstance(M2.signals["q"], h.Signal)
    assert isinstance(M2.instances["i"], h.Instance)

    # Test the getattr magic for signals, ports, and instances
    assert isinstance(M2.i, h.Instance)
    assert M2.instances["i"] is M2.i
    assert isinstance(M2.q, h.Signal)
    assert M2.signals["q"] is M2.q
    assert isinstance(M1.s, h.Signal)
    assert M1.ports["s"] is M1.s


def test_generator1():
    import hdl21 as h

    @dataclass
    class MyParams:
        a: int = 5

    @h.generator
    def gen1(params: MyParams) -> h.Module:
        m = h.Module()
        m.i = h.Input()
        return m

    m = h.elaborate(gen1, MyParams(a=3))

    assert m.name == "gen1"
    assert isinstance(m.i, h.Signal)
    assert m._genparams == MyParams(a=3)
