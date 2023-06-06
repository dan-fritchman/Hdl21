""" 
# Fully Differential OTA Example 

Highlights the capacity to use `Diff` signals and `Pair`s of instances 
for differential circuits. 

"""

import sys
from copy import deepcopy
import hdl21 as h


""" 
Create a small "PDK" consisting of an externally-defined Nmos and Pmos transistor. 
Real versions will have some more parameters; these just have multiplier "m". 
"""


@h.paramclass
class MosParams:
    m = h.Param(dtype=int, desc="Transistor Multiplier")


nmos = h.ExternalModule(
    name="nmos",
    desc="Nmos Transistor (Multiplier Param Only!)",
    port_list=deepcopy(h.Mos.port_list),
    paramtype=MosParams,
)
pmos = h.ExternalModule(
    name="pmos",
    desc="Pmos Transistor (Multiplier Param Only!)",
    port_list=deepcopy(h.Mos.port_list),
    paramtype=MosParams,
)


@h.generator
def DiffOta(_: h.HasNoParams) -> h.Module:
    """# Fully Differential OTA
    With input-stage common-mode feedback."""

    @h.module
    class DiffOta:
        # IO Interface
        VDD, VSS = 2 * h.Input()
        inp = h.Diff(desc="Differential Input", port=True, role=h.Diff.Roles.SINK)
        out = h.Diff(desc="Differential Output", port=True, role=h.Diff.Roles.SOURCE)
        vg, ibias = 2 * h.Input()

        # Internal Signals
        out1 = h.Diff(desc="First Stage Output")
        pbias = h.Signal(desc="Pmos Gate Bias")

        # Input Stage & CMFB Bias
        xbias_input = nmos(m=1)(g=vg, s=VSS, b=VSS)
        xinput_pair = h.Pair(nmos(m=10))(d=out1, g=inp, s=xbias_input.d, b=VSS)
        xinput_load = h.Pair(pmos(m=3))(d=out1, g=pbias, s=VDD, b=VDD)

        # Output Stage
        xpout = h.Pair(pmos(m=16))(d=out, g=out1, s=VDD, b=VDD)
        xnout = h.Pair(nmos(m=4))(d=out, g=ibias, s=VSS, b=VSS)

        # Biasing
        xndiode = nmos(m=1)(d=ibias, g=ibias, s=VSS, b=VSS)
        xnsrc = nmos(m=1)(d=pbias, g=ibias, s=VSS, b=VSS)
        xpdiode = pmos(m=6)(d=pbias, g=pbias, s=VDD, b=VDD)

        # Compensation Network
        xcomp = h.Pair(Compensation)(a=out, b=out1, VDD=VDD, VSS=VSS)

    return DiffOta


@h.module
class CapCell:
    """# Compensation Capacitor Cell"""

    p, n, VDD, VSS = 4 * h.Port()
    # FIXME: internal content! Using tech-specific `ExternalModule`s


@h.module
class ResCell:
    """# Compensation Resistor Cell"""

    p, n, sub = 3 * h.Port()
    # FIXME: internal content! Using tech-specific `ExternalModule`s


@h.module
class Compensation:
    """# Single Ended RC Compensation Network"""

    a, b, VDD, VSS = 4 * h.Port()
    r = ResCell(p=a, sub=VDD)
    c = CapCell(p=r.n, n=b, VDD=VDD, VSS=VSS)


def main():
    h.netlist(DiffOta(), sys.stdout)


if __name__ == "__main__":
    main()
