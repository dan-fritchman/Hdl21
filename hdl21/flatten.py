"""
Flatten a module by moving all nested instances, ports and signals to the root level.

See function `flatten()` for details.
"""

import copy
from dataclasses import dataclass, field, replace
from typing import Dict, Generator, Tuple, Union

import hdl21 as h


def _walk_conns(conns, parents=tuple()):
    for key, val in conns.items():
        if isinstance(val, dict):
            yield from _walk_conns(val, parents + (key,))
        else:
            yield parents + (key,), val


def _flat_conns(conns):
    return {":".join(reversed(path)): value.name for path, value in _walk_conns(conns)}


@dataclass
class _PrimitiveNode:
    inst: h.Instance
    path: Tuple[h.Module, ...] = tuple()
    conns: Dict[str, h.Signal] = field(default_factory=dict)  # type: ignore

    def __str__(self):
        name = self.make_name()
        path = [p.name for p in self.path]
        conns = _flat_conns(self.conns)
        return str(dict(name=name, path=path, conns=conns))

    def make_name(self):
        return ":".join([p.name or "_" for p in self.path])


def walk(
    m: h.Module,
    parents=tuple(),
    conns=None,
) -> Generator[_PrimitiveNode, None, None]:
    if not conns:
        conns = {**m.signals, **m.ports}
    for inst in m.instances.values():
        new_conns = {}
        new_parents = parents + (inst,)
        for src_port_name, sig in inst.conns.items():
            if isinstance(sig, h.Signal):
                key = sig.name
            else:
                raise ValueError(f"unexpected signal type: {type(sig)}")

            new_sig_name = ":".join([p.name for p in parents] + [key])
            if key in conns:
                target_sig = conns[key]
            elif key in m.signals:
                target_sig = replace(m.signals[key], name=new_sig_name)
            elif key in m.ports:
                target_sig = replace(m.ports[key], name=new_sig_name)
            else:
                raise ValueError(f"signal {key} not found")
            new_conns[src_port_name] = target_sig

        if isinstance(inst.of, h.PrimitiveCall):
            yield _PrimitiveNode(inst, new_parents, new_conns)
        else:
            yield from walk(inst.of, new_parents, new_conns)


def _find_signal_or_port(m: h.Module, name: str) -> h.Signal:
    """Find a signal or port by name"""

    if (port := m.ports.get(name, None)) is not None:
        return port
    elif (sig := m.signals.get(name, None)) is not None:
        return sig
    else:
        raise ValueError(f"Signal {name} not found in module {m.name}")


def is_flat(m: Union[h.Instance, h.Instantiable]) -> bool:
    if isinstance(m, h.Instance):
        return is_flat(m.of)
    elif isinstance(m, (h.PrimitiveCall, h.GeneratorCall, h.ExternalModuleCall)):
        return True
    elif isinstance(m, h.Module):
        insts = m.instances.values()
        return all(
            isinstance(inst.of, (h.PrimitiveCall, h.ExternalModuleCall))
            for inst in insts
        )
    else:
        raise ValueError(f"Unexpected type {type(m)}")


def flatten(m: h.Module) -> h.Module:
    r"""Flatten a module by moving all nested instances, ports and signals to the root level.

    For example, if we have a buffer module with two inverters, `inv_1` and `inv_2`, each with
    two transistors, `pmos` and `nmos`, the module hierarchy looks like this:
    All signals and ports will be moved to the root level too.

    ```
    buffer
    ├── inv_1
    │   ├── pmos
    │   └── nmos
    └── inv_2
        ├── pmos
        └── nmos
    ```

    This function will flatten the module to the following structure:

    ```
    buffer_flat
    ├── inv_1:pmos
    ├── inv_1:nmos
    ├── inv_2:pmos
    └── inv_2:nmos
    ```

    Nested signals and ports will be renamed and moved to the root level as well. For example, say a
    module with two buffers, `buffer_1` and `buffer_2`, each with two inverters. On the top level,
    the original ports `vdd`, `vss`, `vin` and `vout` are preserved. Nested signals and ports such
    the connection between two buffers, the internal signal between two inverters in buffer 1 will
    be renamed and moved to the root level as `buffer_1_vout`, `buffer_1:inv_1_vout`,
    `buffer_2:inv_1_vout`.

    See tests/test_flatten.py for more examples.
    """

    m = h.elaborate(m)
    if is_flat(m):
        return m

    # recursively walk the module and collect all primitive instances
    nodes = list(walk(m))

    # NOTE: should we rename the module here?
    new_module = h.Module((m.name or "module") + "_flat")
    for port in m.ports.values():
        new_module.add(copy.copy(port))

    # add all signals to the root level
    for n in nodes:
        for sig in n.conns.values():
            sig_name = sig.name
            if sig_name not in new_module.ports:
                new_module.add(copy.copy(sig))

    # add all connections to the root level with names resolved
    for n in nodes:
        new_inst = new_module.add(n.inst.of(), name=n.make_name())

        for src_port_name, sig in n.conns.items():
            matching_sig = _find_signal_or_port(new_module, sig.name)
            new_inst.connect(src_port_name, matching_sig)

    return new_module
