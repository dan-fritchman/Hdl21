import sys

import hdl21 as h
from hdl21.diff import Diff, diff_inst


@h.paramclass
class AmpParams:
    nmos = h.Param(dtype=h.Instantiable, desc="Nmos Module")
    pmos = h.Param(dtype=h.Instantiable, desc="Pmos Module")


@h.generator
def FoldedCascode(params: AmpParams) -> h.Module:
    """ Folded Cascode Op-Amp """

    nmos, pmos = params.nmos, params.pmos

    @h.module
    class FoldedCascode:
        # Declare I/O
        inp = Diff(port=True)
        out = h.Output()
        VDD, VSS, ibias = h.Inputs(3)
        # Internal Signals
        outm = h.Signal()

        # Input pair and bias
        nibias = 2 * nmos(s=VSS, b=VSS)
        ninp = diff_inst(nmos)(g=inp, s=nibias.d, b=VSS)
        pild = diff_inst(pmos)(d=ninp.d, s=VDD, b=VDD)

        # Cascode Stack
        psrc = diff_inst(pmos)(d=ninp.d, s=VDD, b=VDD)
        pcas = diff_inst(pmos)(d=[out, outm], s=psrc.d, b=VDD)
        ncas = diff_inst(nmos)(d=[out, outm], b=VSS)
        nsrc = diff_inst(nmos)(d=ncas.s, g=outm, s=VSS, b=VSS)

        # Bias mirrors
        ncd = nmos(g=ibias, d=ibias, b=VSS)
        nsd = nmos(g=ncd.s, d=ncd.s, s=VSS, b=VSS)
        ncas.g = ncd.g
        nsrc.g = nibias.g = nsd.g
        nbm = nmos(g=ibias, s=VSS, b=VSS)
        pcd = pmos(d=nbm.d, g=nbm.d, b=VDD)
        pcas.g = pcd.g
        psd = pmos(d=pcd.s, g=pcd.s, s=VDD, b=VDD)
        psrc.g = psd.g

    return FoldedCascode


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
