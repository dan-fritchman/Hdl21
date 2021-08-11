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


def external_factory(name: str, port_names: Sequence[str]) -> h.ExternalModule:
    return h.ExternalModule(name, f'external_module_{name}',
                            [h.Inout(name=n) for n in port_names])


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
    res_prim, res_params = primitive_factory("rupolym_m", ["w", "l"], ["PLUS", "MINUS"])
    res_prim = external_factory("rupolym_m", ["PLUS", "MINUS"])
    params = RLadderParams(
        nseg=15, res=res_prim, res_params=res_params(w=4, l=10), res_conns=dict(PLUS='P', MINUS='N'))
    proto = h.to_proto(h.elaborate(rladder, params))
    h.netlist("", proto)


if __name__ == '__main__':
    generate()
