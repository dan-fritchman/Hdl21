"""
# SkyWater 130nm OSS PDK Plug-In 

Unit Tests
"""

from io import StringIO
import hdl21 as h
from . import pdk as sky130
from .pdk import modules as s


def test_default():
    h.pdk.set_default(sky130)
    assert h.pdk.default() is sky130


def mosmodule():
    # Create a simple Module with each of the default-param Mos types
    hasmos = h.Module(name="hasmos")
    z = hasmos.z = h.Signal()
    hasmos.n = h.Nmos(h.MosParams())(d=z, g=z, s=z, b=z)
    hasmos.p = h.Pmos(h.MosParams())(d=z, g=z, s=z, b=z)

    # Checks on the initial Module
    assert isinstance(hasmos.n, h.Instance)
    assert isinstance(hasmos.p, h.Instance)
    assert isinstance(hasmos.n.of, h.PrimitiveCall)
    assert isinstance(hasmos.p.of, h.PrimitiveCall)

    return hasmos


def test_compile():
    hasmos = mosmodule()

    # Compile it for the PDK
    sky130.compile(hasmos)

    # And check what came back
    assert isinstance(hasmos.n, h.Instance)
    assert isinstance(hasmos.p, h.Instance)
    assert isinstance(hasmos.n.of, h.ExternalModuleCall)
    assert isinstance(hasmos.p.of, h.ExternalModuleCall)
    assert isinstance(hasmos.n.of.params, sky130.Sky130MosParams)
    assert isinstance(hasmos.p.of.params, sky130.Sky130MosParams)


def test_netlist():
    hasmos = mosmodule()

    # Netlist it for the PDK
    sky130.compile(hasmos)
    h.netlist(hasmos, StringIO(), fmt="spice")
    h.netlist(hasmos, StringIO(), fmt="spectre")
    h.netlist(hasmos, StringIO(), fmt="verilog")


def test_module1():

    mp = sky130.Sky130MosParams()

    @h.module
    class HasXtors:
        # Instantiate each transistor, with the default parameter values
        ns = s.sky130_fd_pr__nfet_01v8(mp)()
        nl = s.sky130_fd_pr__nfet_01v8_lvt(mp)()
        ps = s.sky130_fd_pr__pfet_01v8(mp)()
        ph = s.sky130_fd_pr__pfet_01v8_hvt(mp)()


def test_walker_contents():
    from hdl21.tests.content import walker_test_content

    content = walker_test_content()
    sky130.compile(content)
