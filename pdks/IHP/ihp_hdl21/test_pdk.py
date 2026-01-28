"""
# IHP SG13G2 130nm BiCMOS PDK Plug-In

Unit Tests
"""

from io import StringIO
import hdl21 as h
from . import pdk_logic as ihp
import ihp_hdl21.primitives as s
from hdl21.prefix import µ
from hdl21.primitives import *


def test_default():
    """Test setting IHP as default PDK."""
    h.pdk.set_default(ihp)
    assert h.pdk.default() is ihp


def mos_primitives_module():
    """Create module with all MOS transistors."""

    @h.module
    class MosPrimitives:
        """Module with all MOS FETs supported by the IHP PDK package."""

        z = h.Signal(desc="Sole signal connected to everything")

        # Low-voltage (1.2V core) transistors
        lv_nmos = h.Mos(tp=MosType.NMOS, vth=MosVth.STD, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )
        lv_pmos = h.Mos(tp=MosType.PMOS, vth=MosVth.STD, family=MosFamily.CORE)(
            d=z, g=z, s=z, b=z
        )

        # High-voltage (3.3V I/O) transistors
        hv_nmos = h.Mos(tp=MosType.NMOS, vth=MosVth.STD, family=MosFamily.IO)(
            d=z, g=z, s=z, b=z
        )
        hv_pmos = h.Mos(tp=MosType.PMOS, vth=MosVth.STD, family=MosFamily.IO)(
            d=z, g=z, s=z, b=z
        )

    return MosPrimitives


def resistor_primitives_module():
    """Create module with all resistor types."""

    @h.module
    class ResistorPrimitives:
        """Module with all resistor primitives supported by the IHP PDK package."""

        z = h.Signal(desc="Sole signal connected to everything")

        # IHP resistors are 3-terminal (p, n, b)
        res_rsil = h.ThreeTerminalResistor(model="rsil")(p=z, n=z, b=z)
        res_rhigh = h.ThreeTerminalResistor(model="rhigh")(p=z, n=z, b=z)
        res_rppd = h.ThreeTerminalResistor(model="rppd")(p=z, n=z, b=z)

    return ResistorPrimitives


def capacitor_primitives_module():
    """Create module with MIM capacitors."""

    @h.module
    class CapacitorPrimitives:
        """Module with MIM capacitor primitives supported by the IHP PDK package."""

        z = h.Signal(desc="Sole signal connected to everything")

        # 2-terminal MIM capacitor
        cap_cmim = h.PhysicalCapacitor(model="cap_cmim")(p=z, n=z)
        # 3-terminal RF MIM capacitor
        cap_rfcmim = h.ThreeTerminalCapacitor(model="cap_rfcmim")(p=z, n=z, b=z)

    return CapacitorPrimitives


def bjt_primitives_module():
    """Create module with HBT and PNP transistors."""

    @h.module
    class BjtPrimitives:
        """Module with bipolar transistor primitives supported by the IHP PDK package."""

        z = h.Signal(desc="Sole signal connected to everything")

        # PNP (3-terminal)
        pnp = h.Pnp(model="pnpMPA")(e=z, b=z, c=z)

        # Note: HBTs have 4 terminals (c, b, e, bn) which doesn't match
        # standard Hdl21 Bipolar primitive. Use direct instantiation for HBTs.

    return BjtPrimitives


def diode_primitives_module():
    """Create module with diode and ESD devices."""

    @h.module
    class DiodePrimitives:
        """Module with diode primitives supported by the IHP PDK package."""

        z = h.Signal(desc="Sole signal connected to everything")

        # Schottky diode (note: actually 3-terminal but we map to 2-terminal)
        schottky = h.Diode(model="schottky_nbl1")(p=z, n=z)

    return DiodePrimitives


def _compile_and_test(prims: h.Module, paramtype: h.paramclass):
    """Compile module and verify instances have correct parameter types."""

    # Compile
    ihp.compile(prims)

    # Test each instance
    for k in prims.namespace:
        if k != "z":
            assert isinstance(prims.namespace[k], h.Instance)
            assert isinstance(prims.namespace[k].of, h.ExternalModuleCall)
            assert isinstance(prims.namespace[k].of.params, paramtype)


def test_compile_mos():
    """Test MOS transistor compilation."""
    _compile_and_test(mos_primitives_module(), (ihp.IhpMosParams, ihp.IhpMosHvParams))


def test_compile_resistors():
    """Test resistor compilation."""
    _compile_and_test(resistor_primitives_module(), ihp.IhpResParams)


def test_compile_capacitors():
    """Test capacitor compilation."""
    _compile_and_test(capacitor_primitives_module(), ihp.IhpCapParams)


def test_compile_bjt():
    """Test BJT compilation."""
    _compile_and_test(bjt_primitives_module(), ihp.IhpPnpParams)


def test_compile_diodes():
    """Test diode compilation."""
    _compile_and_test(diode_primitives_module(), ihp.IhpDiodeParams)


def _netlist(prims):
    """Compile and netlist a module."""

    # Compile for PDK
    ihp.compile(prims)
    # Generate SPICE netlist
    h.netlist(prims, StringIO(), fmt="spice")


def test_netlist():
    """Test SPICE netlist generation for all device types."""

    _netlist(mos_primitives_module())
    _netlist(resistor_primitives_module())
    _netlist(capacitor_primitives_module())
    _netlist(bjt_primitives_module())
    # Note: diode_primitives_module() is not tested for netlisting because
    # IHP's Schottky diode is 3-terminal (a, c, s) but Hdl21's Diode primitive
    # is 2-terminal (p, n). Use direct instantiation for 3-terminal diodes.


def test_mos_module():
    """Test direct MOS module instantiation."""

    p = ihp.IhpMosParams()
    q = ihp.IhpMosHvParams()

    @h.module
    class HasMos:
        lv_nmos = s.LV_NMOS(p)()
        lv_pmos = s.LV_PMOS(p)()
        hv_nmos = s.HV_NMOS(q)()
        hv_pmos = s.HV_PMOS(q)()


def test_resistor_module():
    """Test direct resistor module instantiation."""

    p = ihp.IhpResParams()

    @h.module
    class HasResistors:
        rsil = s.RSIL(p)()
        rhigh = s.RHIGH(p)()
        rppd = s.RPPD(p)()


def test_capacitor_module():
    """Test direct capacitor module instantiation."""

    p = ihp.IhpCapParams()
    q = ihp.IhpVaricapParams()

    @h.module
    class HasCapacitors:
        cmim = s.CAP_CMIM(p)()
        rfcmim = s.CAP_RFCMIM(p)()
        svaricap = s.SVARICAP(q)()


def test_hbt_module():
    """Test direct HBT module instantiation."""

    p = ihp.IhpHbtParams()

    @h.module
    class HasHbts:
        npn13g2 = s.NPN13G2(p)()
        npn13g2l = s.NPN13G2L(p)()
        npn13g2v = s.NPN13G2V(p)()
        npn13g2_5t = s.NPN13G2_5T(p)()
        npn13g2l_5t = s.NPN13G2L_5T(p)()
        npn13g2v_5t = s.NPN13G2V_5T(p)()


def test_pnp_module():
    """Test direct PNP module instantiation."""

    p = ihp.IhpPnpParams()

    @h.module
    class HasPnp:
        pnpmpa = s.PNPMPA(p)()


def test_diode_module():
    """Test direct diode module instantiation."""

    p = ihp.IhpDiodeParams()
    q = ihp.IhpEsdParams()

    @h.module
    class HasDiodes:
        schottky = s.SCHOTTKY_NBL1(p)()


def test_esd_module():
    """Test direct ESD device instantiation."""

    p = ihp.IhpEsdParams()

    @h.module
    class HasEsd:
        diodevdd_2kv = s.DIODEVDD_2KV(p)()
        diodevdd_4kv = s.DIODEVDD_4KV(p)()
        diodevss_2kv = s.DIODEVSS_2KV(p)()
        diodevss_4kv = s.DIODEVSS_4KV(p)()


def test_inverter():
    """Test a simple inverter circuit compilation."""

    @h.module
    class Inverter:
        vdd = h.Port()
        vss = h.Port()
        inp = h.Port()
        out = h.Port()

        # Use CORE family for LV transistors
        p = h.Mos(tp=MosType.PMOS, family=MosFamily.CORE)(
            g=inp, d=out, s=vdd, b=vdd
        )
        n = h.Mos(tp=MosType.NMOS, family=MosFamily.CORE)(
            g=inp, d=out, s=vss, b=vss
        )

    # Compile
    ihp.compile(Inverter)

    # Verify compilation
    assert isinstance(Inverter.p.of, h.ExternalModuleCall)
    assert isinstance(Inverter.n.of, h.ExternalModuleCall)
    assert "sg13_lv_pmos" in Inverter.p.of.module.name
    assert "sg13_lv_nmos" in Inverter.n.of.module.name

    # Generate netlist
    h.netlist(Inverter, StringIO(), fmt="spice")


def test_io_buffer():
    """Test an I/O buffer with HV transistors."""

    @h.module
    class IoBuffer:
        vdd = h.Port()
        vss = h.Port()
        inp = h.Port()
        out = h.Port()

        # Use IO family for HV transistors
        p = h.Mos(tp=MosType.PMOS, family=MosFamily.IO)(
            g=inp, d=out, s=vdd, b=vdd
        )
        n = h.Mos(tp=MosType.NMOS, family=MosFamily.IO)(
            g=inp, d=out, s=vss, b=vss
        )

    # Compile
    ihp.compile(IoBuffer)

    # Verify compilation
    assert isinstance(IoBuffer.p.of, h.ExternalModuleCall)
    assert isinstance(IoBuffer.n.of, h.ExternalModuleCall)
    assert "sg13_hv_pmos" in IoBuffer.p.of.module.name
    assert "sg13_hv_nmos" in IoBuffer.n.of.module.name


def test_walker_contents():
    """Test walker with standard content."""
    from hdl21.tests.content import walker_test_content

    content = walker_test_content()
    ihp.compile(content)
