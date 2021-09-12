import sys

import hdl21 as h


@h.interface
class Diff:  # Differential Signal Interface
    p = h.Signal()
    n = h.Signal()


@h.paramclass
class AmpParams:
    nmos = h.Param(dtype=h.Instantiable, desc="Nmos Module")
    pmos = h.Param(dtype=h.Instantiable, desc="Pmos Module")


@h.generator
def FiveXtorAmp(params: AmpParams) -> h.Module:
    """ "Five-Transistor" Op-Amp """

    nmos, pmos = params.nmos, params.pmos

    @h.module
    class Amp:
        # First declare our I/O
        inp = Diff(port=True)
        out = Diff(port=True)
        VDD, VSS, ibias, vbias = h.Inputs(4)

        # Bias mirror
        ndiode = nmos(g=ibias, d=ibias, s=VSS, b=VSS)
        nibias = nmos(g=ibias, s=VSS, b=VSS)
        # Input pair
        ninp = nmos(g=inp.p, d=out.n, s=nibias.d, b=VSS)
        ninn = nmos(g=inp.n, d=out.p, s=nibias.d, b=VSS)
        # Output load
        pldp = pmos(g=vbias, d=out.p, s=VDD, b=VDD)
        pldm = pmos(g=vbias, d=out.n, s=VDD, b=VDD)

    return Amp


PdkNmos = h.ExternalModule(
    name="PdkNmos",
    desc="PDK NMOS Transistor",
    port_list=[
        h.Inout(name="d"),
        h.Inout(name="g"),
        h.Inout(name="s"),
        h.Inout(name="b"),
    ],
    paramtype=h.HasNoParams,
)
PdkPmos = h.ExternalModule(
    name="PdkPmos",
    desc="PDK PMOS Transistor",
    port_list=[
        h.Inout(name="d"),
        h.Inout(name="g"),
        h.Inout(name="s"),
        h.Inout(name="b"),
    ],
    paramtype=h.HasNoParams,
)


def generate():
    """ Main function, generating and netlisting. """

    params = AmpParams(nmos=PdkNmos(h.NoParams), pmos=PdkPmos(h.NoParams),)
    proto = h.to_proto(h.elaborate(FiveXtorAmp(params)))
    h.netlist(proto, sys.stdout)


if __name__ == "__main__":
    generate()
