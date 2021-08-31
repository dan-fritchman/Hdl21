import sys
from typing import Dict, Any, Tuple, Sequence

import hdl21 as h


@h.paramclass
class RLadderParams:
    nseg: int = h.Param(dtype=int, desc="Number of segments")
    res: h.Module = h.Param(dtype=Any, desc="Resistor Primitive")
    res_params: Dict[str, Any] = h.Param(dtype=Any, desc="Resistor params")
    res_conns: Dict[str, str] = h.Param(
        dtype=dict,
        desc="A dict mapping res ports to value P, N and any other res ports to pass through")


@h.generator
def rladder(params: RLadderParams) -> h.Module:

    # Base Module, we'll just declare IO
    @h.module
    class RLadder:
        top = h.Inout()
        bot = h.Inout()
        taps = h.Output(width=params.nseg - 1)

    # A list of all the nets, from the bottom to the top
    netnames = [RLadder.bot] + [RLadder.taps[i] for i in range(params.nseg-1)] + [RLadder.top]
    pconns = [k for k, v in params.res_conns.items() if v == 'P']  # All the ports of res that connect to P
    nconns = [k for k, v in params.res_conns.items() if v == 'N']  # All the ports of res that connect to N
    conns = params.res_conns.copy()  # Make a copy we will mutate
    for i, net in enumerate(netnames[:-1]):
        for k in pconns:
            conns[k] = netnames[i + 1]  # Connect P to the P net for this resistor
        for k in nconns:
            conns[k] = netnames[i]  # Connect N to the N net for this resistor
        # Set each resistor of RLadder as an attibute by calling the generator then adding conns
        setattr(RLadder, f'R{i}', params.res(params.res_params)(**conns))

    return RLadder


@h.paramclass
class PassGateParams:
    nmos: h.Module = h.Param(dtype=Any, desc="NMOS generator")
    nmos_params: Dict[str, Any] = h.Param(dtype=Any, desc="PMOS Parameters")
    pmos: h.Module = h.Param(dtype=Any, desc="PMOS generator")
    pmos_params: Dict[str, Any] = h.Param(dtype=Any, desc="PMOS parameters")


@h.generator
def passgate(params: PassGateParams) -> h.Module:
    @h.module
    class PassGate:
        source = h.Inout()
        drain = h.Inout()
    if params.pmos is not None:
        setattr(PassGate, f'VDD', h.Inout())
        setattr(PassGate, f'en_b', h.Input())
        setattr(PassGate, f'PSW', params.pmos(params.pmos_params)(
            D=PassGate.drain, S=PassGate.source, G=PassGate.en_b, B=PassGate.VDD))
    if params.nmos is not None:
        setattr(PassGate, f'VSS', h.Inout())
        setattr(PassGate, f'en', h.Input())
        setattr(PassGate, f'NSW', params.nmos(params.nmos_params)(
            D=PassGate.drain, S=PassGate.source, G=PassGate.en, B=PassGate.VSS))

    return PassGate


@h.generator
def mux(params: PassGateParams) -> h.Module:
    @h.module
    class Mux:
        sourceA = h.Input()
        sourceB = h.Input()
        out = h.Output()
        ctrl = h.Input()
        ctrl_b = h.Input()

    aconns, bconns = dict(source=Mux.sourceA, drain=Mux.out), dict(source=Mux.sourceB, drain=Mux.out)
    if params.pmos is not None:
        setattr(Mux, f'VDD', h.Inout())
        aconns['VDD'] = Mux.VDD
        aconns['en_b'] = Mux.ctrl_b
        bconns['VDD'] = Mux.VDD
        bconns['en_b'] = Mux.ctrl
    if params.nmos is not None:
        setattr(Mux, f'VSS', h.Inout())
        aconns['VSS'] = Mux.VSS
        aconns['en'] = Mux.ctrl
        bconns['VSS'] = Mux.VSS
        bconns['en'] = Mux.ctrl_b
    setattr(Mux, f'passgate_a', passgate(params)(**aconns))
    setattr(Mux, f'passgate_b', passgate(params)(**bconns))
    return Mux


@h.paramclass
class MuxTreeParams:
    nbit: int = h.Param(dtype=int, desc="Number of bits")
    mux_params: Any = h.Param(dtype=Any, desc="Parameters for the MUX generator")


@h.generator
def mux_tree(params: MuxTreeParams) -> h.Module:
    n_inputs = 2 ** params.nbit
    p_ctrl = params.mux_params.nmos is not None
    n_ctrl = params.mux_params.pmos is not None

    # Base module
    @h.module
    class MuxTree:
        out = h.Output()
        v_in = h.Input(width=n_inputs)
        ctrl = h.Input(width=params.nbit)
        ctrl_b = h.Input(width=params.nbit)

    base_mux_conns = dict()
    if p_ctrl:
        setattr(MuxTree, 'VSS', h.Inout())
        base_mux_conns['VSS'] = MuxTree.VSS
    if n_ctrl:
        setattr(MuxTree, 'VDD', h.Inout())
        base_mux_conns['VDD'] = MuxTree.VDD

    # Build the MUX tree layer by layer
    curr_input = MuxTree.v_in
    for layer in range(params.nbit-1, -1, -1):
        layer_mux_conns = base_mux_conns.copy()
        layer_mux_conns['ctrl'] = MuxTree.ctrl[layer]
        layer_mux_conns['ctrl_b'] = MuxTree.ctrl_b[layer]
        if layer != 0:
            setattr(MuxTree, f'sig_{layer}', h.Signal(width=2 ** layer))
            curr_output = getattr(MuxTree, f'sig_{layer}')
        else:
            curr_output = MuxTree.out
        for mux_idx in range(2**layer):
            mux_conns = layer_mux_conns.copy()
            mux_conns['sourceA'] = curr_input[2 * mux_idx]
            mux_conns['sourceB'] = curr_input[2 * mux_idx + 1]
            mux_conns['out'] = curr_output[mux_idx]
            setattr(MuxTree, f'mux_{layer}_{mux_idx}', mux(params.mux_params)(**mux_conns))
        curr_input = curr_output
    return MuxTree


def external_factory(name: str, param_names: Sequence[str], port_names: Sequence[str]
                     ) -> Tuple[h.ExternalModule, h.Param]:
    """
    Parameters:
        name: should correspond to the expected name in output netlists
        param_names: A list of parameters instances of this external primitive take
        port_names: A list of port names of this external primitive
    Outputs:
        NewPrimitive: An instance of h.Primitive
        NewParamClass: An instance of h.paramclass
    """
    param_attr_dict = {n: h.Param(dtype=Any, desc=f'Gen parameter {n} of {name}') for n in param_names}
    # Dynamically create the parameter class, pass it to the h.paramclass decorator function
    custom_params = h.paramclass(type(f"{name}Params", (), param_attr_dict))
    return h.ExternalModule(name, desc=f'external_module_{name}',
                            port_list=[h.Inout(name=n) for n in port_names]), custom_params


def primitive_factory(name: str, param_names: Sequence[str], port_names: Sequence[str]) -> Tuple[h.Primitive, h.Param]:
    """
    This is a utility function to create a primitive-like objects for use inside generators. The source of these
    objects is assumed to be external.
    Parameters:
        name: should correspond to the expected name in output netlists
        param_names: A list of parameters instances of this external primitive take
        port_names: A list of port names of this external primitive
    Outputs:
        NewPrimitive: An instance of h.Primitive
        NewParamClass: An instance of h.paramclass
    """
    ports = [h.Port(name=n) for n in port_names]
    # Build a dictionary of attributes for our new parameter class
    param_attr_dict = {n: h.Param(dtype=Any, desc=f'Gen parameter {n} of {name}') for n in param_names}
    # Dynamically create the parameter class, pass it to the h.paramclass decorator function
    custom_params = h.paramclass(type(f"{name}Params", (), param_attr_dict))
    return h.Primitive(name=name, desc='Resistor', port_list=ports, paramtype=custom_params), custom_params


def generate():
    res_prim, res_params = external_factory("rupolym_m", ["w", "l"], ["PLUS", "MINUS"])
    params = RLadderParams(
        nseg=15, res=res_prim, res_params=dict(w=4, l=10), res_conns=dict(PLUS='P', MINUS='N'))
    proto = h.to_proto(h.elaborate(rladder, params))
    h.netlist(proto, sys.stdout)

    nmos, nmos_params = external_factory("nch_mac", ['l'], ["D", "G", "S", "B"])
    pmos, pmos_params = external_factory("pch_mac", ['l'], ["D", "G", "S", "B"])
    params = MuxTreeParams(nbit=4, mux_params=PassGateParams(
        nmos=nmos, nmos_params=dict(l=1), pmos=pmos, pmos_params=dict(l=1)))
    proto = h.to_proto(h.elaborate(mux_tree, params))
    h.netlist(proto, sys.stdout)


if __name__ == '__main__':
    generate()
