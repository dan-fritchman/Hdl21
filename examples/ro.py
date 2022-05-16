"""
# Ring Oscillator Example

Controllable Oscillator Module, Based on Gated Inverter Cells from the open-source Sky130 PDK
"""

import sys
import hdl21 as h

# Sky130 Gated-Inverter Cell Declaration
GatedInv = h.ExternalModule(
    name="sky130_fd_sc_hd__einvn_8",
    domain="sky130",
    desc="Sky130 Gated-Inverter Cell",
    port_list=[
        h.Input(name="A"),
        h.Input(name="TEB"),
        h.Output(name="Z"),
        h.Inout(name="vgnd"),
        h.Inout(name="vnb"),
        h.Inout(name="vpb"),
        h.Inout(name="vpwr"),
    ],
)


@h.module
class GatedInvWrapper:
    """ Thin wrapper over `GatedInv` """

    inp, enb, VDD, VSS = h.Inputs(4)
    out = h.Output()
    inv = GatedInv()(A=inp, TEB=enb, Z=out, vgnd=VSS, vnb=VSS, vpb=VDD, vpwr=VDD)


# @h.module
# class GatedInvWrapper:
#     """ An alternate connect-by-assignment version of `GatedInvWrapper` """
#
#     inv = GatedInv()()
#     inv.A = inp = h.Input()
#     inv.TEB = enb = h.Input()
#     inv.vpwr = inv.vpb = VDD = h.Input()
#     inv.vgnd = inv.vnb = VSS = h.Input()
#     inv.Z = out = h.Output()


@h.paramclass
class RoParams:
    stages = h.Param(dtype=int, default=3, desc="Number of stages")
    rows = h.Param(dtype=int, default=3, desc="Number of rows")

    def __post_init_post_parse__(self):
        if not self.stages % 2:
            raise ValueError("stages must be odd")


@h.generator
def Ro(params: RoParams) -> h.Module:
    """ Create a parametric oscillator """
    from hdl21.primitives import IdealCapacitor as C

    ro = h.Module()
    ro.ctrlb = h.Input(width=params.stages * params.rows, desc="Control code")
    ro.osc = h.Output(width=params.stages, desc="Primary Oscillator Output")
    ro.VDD, ro.VSS = h.Inputs(2)

    for row in range(params.rows):
        for stage in range(params.stages):
            # Add a stage
            ro.add(
                GatedInvWrapper(
                    inp=ro.osc[stage],
                    out=ro.osc[(stage + 1) % params.stages],
                    enb=ro.ctrlb[row * params.stages + stage],
                    VSS=ro.VSS,
                    VDD=ro.VDD,
                ),
                name=f"stage{row}{stage}",
            )
            # Add an ideal load capacitor
            c = C(C.Params(c=1e-15))
            ro.add(name=f"c{row}{stage}", val=c(p=ro.osc[stage], n=ro.VSS))

    return ro


@h.generator
def RoTb(params: RoParams) -> h.Module:
    """ Ring Osc Testbench
    Primarily instantiates the RO and a thermometer-encoder for its control code. 

    This module includes a bit of hacking into the SPICE-domain world. 
    It has no ports and is meant to be "the entirety" of a sim, save for analysis and control statements. 
    Don't try it on its own! At minimum, it relies on: 
    * SPICE/ Spectre's concept of "node zero", which it instantiates, and 
    * A SPICE-level parameter `code` which sets the integer control value. 
    This serves as an early case-study for how hdl21 modules and 
    these SPICE-native things can play together (and perhaps how they shouldn't). 
    """
    from hdl21.primitives import V

    # Create our module
    m = h.Module()
    # Add the DUT
    m.ro = Ro(params)()
    # Create signals around it
    m.ro.ctrlb = m.ctrlb = h.Signal(
        width=params.stages * params.rows, desc="Control code"
    )
    m.ro.osc = m.osc = h.Signal(width=params.stages, desc="Primary Oscillator Output")
    m.ro.VDD = m.VDD = h.Signal()
    m.ro.VSS = vss = m.add(h.Signal(name="0"))

    # Create the supply
    m.vvdd = V(V.Params(dc=1.8))(p=m.VDD, n=vss)

    # Now do some SPICE-fu to generate the control code, from a sweep parameter
    for k in range(params.rows * params.stages):
        v = V(V.Params(dc=f"1.8*(code <= {k})"))
        m.add(name=f"vbin{k}b", val=v(p=m.ctrlb[k], n=vss))

    # And don't forget to return em!
    return m


# Netlist this stuff!
ppkg = h.to_proto([RoTb(RoParams())], domain="ro130")
netlist = h.netlist(pkg=ppkg, dest=sys.stdout)
