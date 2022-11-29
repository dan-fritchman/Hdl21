"""
# Ring Oscillator Example

Controllable Oscillator Module, Based on Gated Inverter Cells from the open-source Sky130 PDK
"""

import sys
import hdl21 as h
from hdl21.prefix import m
from hdl21.primitives import V, C

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
    """Thin wrapper over `GatedInv`"""

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
    """# Ring Oscillator Parameters"""

    stages = h.Param(dtype=int, default=3, desc="Number of stages")
    rows = h.Param(dtype=int, default=3, desc="Number of rows")


@h.generator
def Ro(params: RoParams) -> h.Module:
    """# Parametric ring oscillator generator"""
    if not params.stages % 2:
        raise ValueError("stages must be odd")

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


@h.paramclass
class TbParams:
    """# Ring Oscillator Testbench Parameters"""

    ro = h.Param(dtype=RoParams, default=RoParams(), desc="RO Parameters")
    code = h.Param(dtype=int, default=3, desc="Control Code. Default: 3")


@h.generator
def RoTb(params: TbParams) -> h.Module:
    """
    # Ring Oscillator Testbench
    Primarily instantiates the RO and a thermometer-encoded control code driver.
    """

    @h.module
    class RoTb:
        # The IO interface required for any testbench: a sole port for VSS.
        VSS = h.Port()

        # Testbench Signals
        ctrlb = h.Signal(width=params.ro.stages * params.ro.rows, desc="Control code")
        osc = h.Signal(width=params.ro.stages, desc="Primary Oscillator Output")
        VDD = h.Signal(desc="Power Supply")

        # Drive the supply
        vvdd = V(dc=1800 * m)(p=VDD, n=VSS)

        # Instantiate our RO DUT
        ro = Ro(params.ro)(osc=osc, ctrlb=ctrlb, VSS=VSS, VDD=VDD)

    # Now generate a thermometer-encoded control code
    for k in range(params.ro.rows * params.ro.stages):
        dc = 1800 * m if k <= params.code else 0 * m
        RoTb.add(name=f"vctrl{k}b", val=V(dc=dc)(p=RoTb.ctrlb[k], n=RoTb.VSS))

    # And don't forget to return the module!
    return RoTb


def main():
    # Netlist this stuff!
    h.netlist(RoTb(h.Default), dest=sys.stdout)


if __name__ == "__main__":
    main()
