""" 
Serial Link Transmit & Receive Example 
"""

from enum import Enum, auto
import hdl21 as h

import sitepdks as _


Inv = h.ExternalModule(
    name="Inv",
    port_list=[h.Input(name="i"), h.Output(name="z"),],
    desc="Generic Inverter",
)
And2 = h.ExternalModule(
    name="And2",
    port_list=[h.Input(name="a"), h.Input(name="b"), h.Output(name="z"),],
    desc="Generic 3-Input And Gate",
)
And3 = h.ExternalModule(
    name="And3",
    port_list=[
        h.Input(name="a"),
        h.Input(name="b"),
        h.Input(name="c"),
        h.Output(name="z"),
    ],
    desc="Generic 3-Input And Gate",
)
TriInv = h.ExternalModule(
    name="TriInv",
    port_list=[h.Input(name="i"), h.Input(name="en"), h.Output(name="z"),],
    desc="Generic Tri-State Inverter",
)
Flop = h.ExternalModule(
    name="Flop",
    port_list=[h.Input(name="d"), h.Input(name="clk"), h.Output(name="q"),],
    desc="Generic Rising-Edge D Flip Flop",
)
FlopResetLow = h.ExternalModule(
    name="FlopResetLow",
    port_list=[
        h.Input(name="d"),
        h.Input(name="clk"),
        h.Input(name="rstn"),
        h.Output(name="q"),
    ],
    desc="Rising-Edge D Flip Flop. Output low with reset asserted.",
)
FlopResetHigh = h.ExternalModule(
    name="FlopResetHigh",
    port_list=[
        h.Input(name="d"),
        h.Input(name="clk"),
        h.Input(name="rstn"),
        h.Output(name="q"),
    ],
    desc="Rising-Edge D Flip Flop. Output high with reset asserted.",
)
Latch = h.ExternalModule(
    name="Latch",
    port_list=[h.Input(name="d"), h.Input(name="clk"), h.Output(name="q"),],
    desc="Generic Active High Level-Sensitive Latch",
)


@h.bundle
class Diff:
    """ Differential Bundle """

    class Roles(Enum):
        SOURCE = auto()
        SINK = auto()

    p, n = h.Signals(2, src=Roles.SOURCE, dest=Roles.SINK)


@h.paramclass
class Width:
    """ Parameter class for Generators with a single integer-valued `width` parameter. """

    width = h.Param(dtype=int, desc="Parametric Width", default=1)


@h.module
class OneHotEncoder2to4:
    """ 
    # One-Hot Encoder
    2b to 4b with enable. 
    Also serves as the base-case for the recursive `OneHotEncoder` generator. 
    All outputs are low if enable-input `en` is low. 
    """

    # IO Interface
    en = h.Input(width=1, desc="Enable input. Active high.")
    bin = h.Input(width=2, desc="Binary valued input")
    th = h.Output(width=4, desc="Thermometer encoded output")

    # Internal Contents
    # Input inverters
    binb = h.Signal(width=2, desc="Inverted binary input")
    invs = 2 * Inv()(i=bin, z=binb)

    # The primary logic: a set of four And3's
    ands = 4 * And3()(
        a=h.Concat(binb[0], bin[0], binb[0], bin[0]),
        b=h.Concat(binb[1], binb[1], bin[1], bin[1]),
        c=en,
        z=th,
    )


@h.generator
def OneHotEncoder(p: Width) -> h.Module:
    """ 
    # One-Hot Encoder Generator 
    Recursively creates a `p.width`-bit one-hot encoder Module comprised of `OneHotEncoder2to4`s. 
    Also generates `OneHotEncoder` Modules for `p.width-2`, `p.width-4`, et al, down to 
    the base case two to four bit Module. 
    """

    if p.width < 2:
        raise ValueError(f"OneHotEncoder {p} width must be > 1")
    if p.width % 2:
        # FIXME: even number of bits only. Add odd cases, eventually
        raise ValueError(f"OneHotEncoder {p} width must be even")
    if p.width == 2:  # Base case: the 2 to 4b encoder
        return OneHotEncoder2to4

    # Recursive case.
    m = h.Module()
    m.en = h.Input(width=1, desc="Enable input. Active high.")
    m.bin = h.Input(width=p.width, desc="Binary valued input")
    m.th = h.Output(width=2 ** p.width, desc="Thermometer encoded output")

    # Thermo-encode the two MSBs, creating select signals for the LSBs
    m.lsb_sel = h.Signal(width=4)
    m.msb_encoder = OneHotEncoder2to4(en=m.en, bin=m.bin[-2:], th=m.lsb_sel)

    # Peel off two bits and recursively generate our child encoder Module
    child = OneHotEncoder(width=p.width - 2)
    # And create four instances of it, enabled by the thermo-decoded MSBs
    m.children = 4 * child(en=m.lsb_sel, bin=m.bin[:-2], th=m.th)

    return m


@h.generator
def OneHotMux(p: Width) -> h.Module:
    """ # One-Hot Selected Mux """

    m = h.Module()

    # IO Interface
    m.inp = h.Input(width=p.width, desc="Primary Input")
    m.sel = h.Input(width=p.width, desc="One-Hot Encoded Selection Input")
    m.out = h.Output(width=1)

    # Internal Implementation
    # Flat bank of `width` tristate inverters
    m.invs = p.width * TriInv()(i=m.inp, en=m.sel, z=m.out)
    return m


@h.generator
def Counter(p: Width) -> h.Module:
    """ # Binary Counter Generator """

    m = h.Module()
    m.clk = h.Input(desc="Primary input. Increments state on each rising edge.")
    m.out = h.Output(width=p.width, desc="Counterer Output State")

    # Divide-by-two stages
    m.invs = p.width * Inv()(i=m.out)
    m.flops = p.width * Flop()(d=m.invs.z, q=m.out, clk=m.clk)
    return m


@h.generator
def OneHotRotator(p: Width) -> h.Module:
    """ # One Hot Rotator 
    A set of `p.width` flops with a one-hot state, 
    which rotates by one bit on each clock cycle. """

    m = h.Module()
    # IO Interface: Clock, Reset, and a `width`-bit One-Hot output
    m.sclk = h.Input(width=1, desc="Serial clock")
    m.rstn = h.Input(width=1, desc="Active-low reset")
    m.out = h.Output(width=p.width, desc="One-hot rotating output")

    m.outb = h.Signal(width=p.width, desc="Internal complementary outputs")
    m.out_invs = p.width * Inv()(i=m.out, z=m.outb)
    m.nxt = h.Signal(width=p.width, desc="Next state; D pins of state flops")

    # The core logic: each next-bit is the AND of the prior bit, and the inverse of the current bit.
    m.ands = p.width * And2()(a=m.outb, b=h.Concat(m.out[1:], m.out[0]), z=m.nxt)
    # LSB flop, output asserted while in reset
    m.lsb_flop = FlopResetHigh()(d=m.nxt[0], clk=m.sclk, q=m.out[0], rstn=m.rstn)
    # All other flops, outputs de-asserted in reset
    m.flops = (p.width - 1) * FlopResetLow()(
        d=m.nxt[1:], clk=m.sclk, q=m.out[1:], rstn=m.rstn
    )

    return m


@h.generator
def TxSerializer(_: h.HasNoParams) -> h.Module:
    """ Transmit Serializer 
    Includes parallel-clock generation divider """

    m = h.Module()
    m.pdata = h.Input(width=16, desc="Parallel Input Data")
    m.sdata = h.Output(width=1, desc="Serial Output Data")
    m.pclk = h.Output(width=1, desc="*Output*, Divided Parallel Clock")
    m.sclk = h.Input(width=1, desc="Input Serial Clock")

    # Create the four-bit counter state, consisting of the parallel clock as MSB,
    # and three internal-signal LSBs.
    m.count_lsbs = h.Signal(width=3, desc="LSBs of Divider-Counterer")
    count = h.Concat(m.count_lsbs, m.pclk)

    m.counter = Counter(width=4)(clk=m.sclk, out=count)
    m.enable_encoder = h.Signal(desc="FIXME: tie this high!")
    m.encoder = OneHotEncoder(width=4)(bin=count, en=m.enable_encoder)
    m.mux = OneHotMux(width=16)(inp=m.pdata, out=m.sdata, sel=m.encoder.th)

    return m


@h.generator
def RxDeSerializer(_: h.HasNoParams) -> h.Module:
    """ RX De-Serializer 
    Includes parallel-clock generation divider """

    m = h.Module()
    m.pdata = h.Output(width=16, desc="Parallel Output Data")
    m.sdata = h.Input(width=1, desc="Serial Input Data")
    m.pclk = h.Output(width=1, desc="*Output*, Divided Parallel Clock")
    m.sclk = h.Input(width=1, desc="Input Serial Clock")

    # Create the four-bit counter state, consisting of the parallel clock as MSB,
    # and three internal-signal LSBs.
    m.count_lsbs = h.Signal(width=3, desc="LSBs of Divider-Counterer")
    count = h.Concat(m.count_lsbs, m.pclk)

    m.counter = Counter(width=4)(clk=m.sclk, out=count)
    m.encoder = OneHotEncoder(width=4)(inp=count)

    # The bank of load-registers, all with data-inputs tied to serial data,
    # "clocked" by the one-hot counter state.
    # Note output `q`s are connected by later instance-generation statements.
    m.load_latches = 8 * Latch()(d=m.sdata, clk=m.encoder.out)
    # The bank of output flops
    m.output_flops = 8 * Flop()(d=m.load_latches.q, q=m.pdata, clk=m.pclk)

    return m


@h.generator
def TxDriver(_: h.HasNoParams) -> h.Module:
    """ Transmit Driver """

    m = h.Module()

    m.data = h.Input(width=1)  # Data Input
    m.pads = Diff(port=True)  # Output pads
    # m.zcal = h.Input(width=32)  # Impedance Control Input
    # FIXME: internal implementation
    # Create the segmented unit drivers
    # m.segments = 32 * TxDriverSegment(pads=pads, en=m.zcal, data=m.data, clk=m.clk)

    return m


@h.module
class SerdesShared:
    """ Serdes 'Shared' Module 
    Central, re-used elements amortized across lanes """

    ...  # So far, empty


@h.bundle
class TxData:
    """ Transmit Data Bundle """

    pdata = h.Input(width=10, desc="Parallel Data Input")
    pclk = h.Output(desc="Output Parallel-Domain Clock")


@h.bundle
class TxConfig:
    """ Transmit Config Bundle """

    ...  # FIXME: contents!


@h.bundle
class TxIo:
    """ Transmit Lane IO """

    pads = Diff(desc="Differential Transmit Pads", role=Diff.Roles.SOURCE)
    data = TxData(desc="Data IO from Core")
    cfg = TxConfig(desc="Configuration IO")


@h.module
class SerdesTxLane:
    """ Transmit Lane """

    # IO
    # io = TxIo(port=True) # FIXME: combined bundle
    # * Pad Interface
    pads = Diff(desc="Differential Transmit Pads", port=True, role=Diff.Roles.SOURCE)
    # * Core Interface
    pdata = h.Input(width=16, desc="Parallel Input Data")
    pclk = h.Output(width=1, desc="*Output*, Divided Parallel Clock")
    # * PLL Interface
    sclk = h.Input(width=1, desc="Input Serial Clock")

    # Internal Implementation
    # Serializer, with internal 8:1 parallel-clock divider
    serializer = TxSerializer()(pdata=pdata, pclk=pclk, sclk=sclk)
    # Output Driver
    driver = TxDriver()(data=serializer.sdata, pads=pads)


@h.module
class SerdesRxLane:
    """ Receive Lane """

    # IO
    # io = RxIo(port=True) # FIXME: combined bundle
    # * Pad Interface
    pads = Diff(desc="Differential Receive Pads", port=True, role=Diff.Roles.SINK)
    # * Core Interface
    pdata = h.Output(width=16, desc="Parallel Output Data")
    pclk = h.Output(width=1, desc="*Output*, Divided Parallel Clock")
    # * PLL Interface
    sclk = h.Input(width=1, desc="Input Serial Clock")

    # # Internal Implementation
    # # Slicers
    # dslicer = Slicer()(inp=pads, out=d, clk=dck)
    # xslicer = Slicer()(inp=pads, out=x, clk=xck)
    # # De-serializer, with internal parallel-clock divider
    # ddser = RxDeSerializer()(sdata=d, pdata=pdata, pclk=pclk, sclk=dck)
    # xdser = RxDeSerializer()(sdata=x, pdata=pdata, pclk=pclk, sclk=dck)
    # # Clock Recovery
    # qck = QuadClock(port=True, role=QuadClock.Roles.SINK)
    # cdr = Cdr()(qck=qck, dck=dck, xck=xck)


@h.bundle
class SerdesCoreIf:
    """ # Serdes to Core Interface """

    ...  #


@h.module
class SerdesLane:
    """ TX + RX Lane """

    # IO Interface
    pads = Diff(desc="Differential Pads", port=True, role=None)
    core_if = SerdesCoreIf(port=True)

    tx = SerdesTxLane()
    rx = SerdesRxLane()


@h.paramclass
class SerdesParams:
    lanes = h.Param(dtype=int, desc="Number of TX & RX Lanes", default=1)


@h.generator
def Serdes(p: SerdesParams) -> h.Module:
    """ Serdes Generator """
    s = h.Module()
    s.lanes = p.lanes * SerdesLane()
    s.shared = SerdesShared()
    return s


def rotator_tb() -> h.Module:
    from hdl21.prefix import m, n, p, f
    from hdl21.primitives import Vpulse, Cap

    tb = h.sim.tb("OneHotRotatorTb")
    tb.dut = OneHotRotator(width=4)()

    tb.cloads = 4 * Cap(Cap.Params(c=1 * f))(p=tb.dut.out, n=tb.VSS)

    tb.vsclk = h.primitives.Vpulse(
        Vpulse.Params(
            delay=0, v1=0, v2=1800 * m, period=2, rise=1 * p, fall=1 * p, width=1,
        )
    )(p=tb.dut.sclk, n=tb.VSS)
    tb.vrstn = h.primitives.Vpulse(
        Vpulse.Params(
            delay=0, v1=0, v2=1800 * m, period=2, rise=1 * p, fall=1 * p, width=1,
        )
    )(p=tb.dut.rstn, n=tb.VSS)

    return tb


def rotator_sim() -> h.sim.Sim:
    from hdl21.prefix import m, n, p, f
    import s130

    sim = h.sim.Sim(tb=rotator_tb())
    sim.add(*s130.install.enough_to_include_tt())
    sim.tran(tstop=1 * n, name="THE_TRAN_DUH")
    return sim


# "Main" Script Action
import sys

# h.netlist(h.to_proto(Serdes(SerdesParams())), dest=sys.stdout)
# h.netlist(h.to_proto(SerdesTxLane), dest=sys.stdout)
# h.netlist(h.to_proto(SerdesRxLane), dest=sys.stdout)
# h.netlist(h.to_proto(OneHotEncoder(width=10)), dest=sys.stdout)
# h.netlist(h.to_proto(OneHotRotator(width=8)), dest=open("scratch/rotator.scs", "w"))
h.netlist(h.to_proto(rotator_tb()), dest=open("scratch/rotator.scs", "w"))

from vlsirtools.spice import SimOptions, SupportedSimulators, ResultFormat

sim = rotator_sim()
# sim.include("/usr/local/google/home/danfritchman/skywater-src-nda/s130/V2.1.1/DIG/scs130hd/V0.0.0/cdl/scs130hd.cdl")
sim.include("scs130hd.cdl")
sim.include("localstuff.sp")
results = sim.run(
    SimOptions(
        simulator=SupportedSimulators.SPECTRE,
        fmt=ResultFormat.SIM_DATA,
        rundir="scratch/",
    )
)

print(results)

