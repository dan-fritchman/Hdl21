""" 
Serial Link Transmit & Receive Example 
"""

from enum import Enum, auto
import hdl21 as h


Inv = h.ExternalModule(
    name="Inv",
    port_list=[h.Input(name="i"), h.Output(name="z"),],
    desc="Generic Inverter",
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
Latch = h.ExternalModule(
    name="Latch",
    port_list=[h.Input(name="d"), h.Input(name="clk"), h.Output(name="q"),],
    desc="Generic Active High Level-Sensitive Latch",
)


@h.generator
def Count16(_: h.HasNoParams) -> h.Module:
    """ Four-Bit, Sixteen-State Rising Edge Counter """

    m = h.Module()
    m.clk = h.Input(desc="Primary Input, Incrementing Output on each rising edge")
    m.out = h.Output(width=4, desc="Counter Output State")

    # Divide-by-two stages
    m.invs = 4 * Inv()(i=m.out)
    m.flops = 4 * Flop()(d=m.invs.z, q=m.out, clk=m.clk)
    return m


@h.generator
def OneHotMux16(_: h.HasNoParams) -> h.Module:
    """ 16-Input, One-Hot Selected Mux """

    m = h.Module()
    m.inp = h.Input(width=16, desc="Primary Input")
    m.sel = h.Input(width=16, desc="One-Hot Encoded Selection Input")
    m.out = h.Output(width=1)

    m.invs = 16 * TriInv()(i=m.inp, en=m.sel, z=m.out)
    return m


@h.generator
def OneHotEncode4to16(_: h.HasNoParams) -> h.Module:
    """ 4 to 16b One-Hot Encoder """
    return h.Module()  # FIXME! the actual contents


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
    m.count_lsbs = h.Signal(width=3, desc="LSBs of Divider-Counter")
    count = h.Concat(m.count_lsbs, m.pclk)

    m.counter = Count16()(clk=m.sclk, out=count)
    m.encoder = OneHotEncode4to16()(inp=count)
    m.mux = OneHotMux16()(inp=m.pdata, out=m.sdata, sel=m.encoder.out)

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
    m.count_lsbs = h.Signal(width=3, desc="LSBs of Divider-Counter")
    count = h.Concat(m.count_lsbs, m.pclk)

    m.counter = Count16()(clk=m.sclk, out=count)
    m.encoder = OneHotEncode4to16()(inp=count)

    # The bank of load-registers, all with data-inputs tied to serial data,
    # "clocked" by the one-hot counter state.
    # Note output `q`s are connected by later instance-generation statements.
    m.load_latches = 16 * Latch()(d=m.sdata, clk=m.encoder.out)
    # The bank of output flops
    m.output_flops = 16 * Flop()(d=m.load_latches.q, q=m.pdata, clk=m.pclk)

    return m


@h.generator
def TxDriver(_: h.HasNoParams) -> h.Module:
    """ Transmit Driver """
    m = h.Module()

    m.data = h.Input(width=2)  # Half-Rate Data Input
    m.clk = h.Input()  # Half-Rate Serial Clock
    m.pads = Diff()  # Output pads
    m.zcal = h.Input(width=32)  # Impedance Control Input
    # Create the segmented unit drivers
    # m.segments = 32 * TxDriverSegment(pads=pads, en=m.zcal, data=m.data, clk=m.clk)

    return m


@h.module
class SerdesShared:
    """ Serdes 'Shared' Module 
    Central, re-used elements amortized across lanes """

    ...  # So far, empty


@h.bundle
class Diff:
    """ Differential Bundle """

    class Roles(Enum):
        # Clock roles: source or sink
        SOURCE = auto()
        SINK = auto()

    p, n = h.Signals(2, src=Roles.SOURCE, dest=Roles.SINK)


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
class SerdesTx:
    """ Transmit Lane """

    io = TxIo(port=True)
    serializer = TxSerializer()(data=io.data)
    driver = TxDriver()()


@h.module
class SerdesRx:
    """ Receive Lane """

    ...  #


@h.module
class SerdesLane:
    """ TX + RX Lane """

    tx = SerdesTx()
    rx = SerdesRx()


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


# "Main" Script Action
import sys

h.netlist(h.to_proto(Serdes(SerdesParams())), dest=sys.stdout)

