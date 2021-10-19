""" 
Serial Link Transmit & Receive Example 
"""

import hdl21 as h


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


@h.module
class SerdesLane:
    tx = SerdesTx()
    rx = SerdesRx()


@h.module
class SerdesShared:
    """ Serdes 'Shared' Module 
    Central, re-used elements amortized across lanes """

    ...  # So far, empty


@h.bundle
class TxData:
    """ Transmit Data Bundle """

    parallel_data = h.Input(width=10)  # Serial Data Input
    parallel_clk = h.Output()  # Internally-Generated Parallel-Domain Clock


@h.bundle
class TxIo:
    """ Transmit Lane IO """

    pads = Diff()  # Transmit Pads
    data = TxData()  # Data from Core
    cfg = TxConfig()  # Configuration


@h.module
class TxSerializer:
    """ Transmit Serializer """

    ...


@h.generator
def TxDriver(_: h.HasNoParams) -> h.Module:
    """ Transmit Driver """
    m = h.Module()

    m.data = h.Input(width=2)  # Half-Rate Data Input
    m.clk = h.Input()  # Half-Rate Serial Clock
    m.pads = h.Diff()  # Output pads
    m.zcal = h.Input(width=32)  # Impedance Control Input
    # Create the segmented unit drivers
    m.segments = 32 * TxDriverSegment(pads=pads, en=m.zcal, data=m.data, clk=m.clk)

    return m


@h.module
class TxDriverSegment:
    """ Transmit Driver Segment
    Voltage-Mode Driver. Includes half-to-full-rate mux and high-z-able unit driver. """

    pads = h.Diff()  # Differential Output Pads
    en = h.Input()  # Enable Input
    data = h.Input(width=2)  # Half-Rate Data Input
    clk = h.Input()  # Half-Rate Serial Clock

    drv_p = TxVmodeDriveInv(ngate=ngate_p, pgate=pgate_p, en=en, data=data_pb)
    drv_n = TxVmodeDriveInv(ngate=ngate_n, pgate=pgate_n, en=en, data=data_pb)


@h.module
class TxVmodeDriveInv:
    """ Voltage-Mode Driver Segment """

    ngate, pgate, VDD, VSS = h.Inputs(4)
    pad = h.Output()

    h.R()(n=pad)  # Output Resistor
    h.Nmos()(d=r.p, g=ngate, s=VDD, b=VDD)  # NMOS Driver
    h.Pmos()(d=r.p, g=pgate, s=VDD, b=VDD)  # PMOS Driver


@h.module
class SerdesTx:
    """ Transmit Lane """

    io = TxIo()
    serializer = TxSerializer(data=io.data, cfg=io.cfg)
    driver = TxDriver()


@h.module
class SerdesRx:
    ...


# "Main" Script Action
Serdes(SerdesParam())
