import copy
import random
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Any, Generator

import tree
from loguru import logger

import hdl21 as h
from hdl21.primitives import MosType


@dataclass
class PrimNode:
    inst: h.Instance
    path: tuple[h.Module, ...] = tuple()
    conns: dict[str, h.Signal] = field(default_factory=dict)  # type: ignore

    def __str__(self):
        name = self.make_name()
        path = [p.name for p in self.path]
        conns = flat_conns(self.conns)
        return str(dict(name=name, path=path, conns=conns))

    def make_name(self):
        return ":".join([p.name or "_" for p in self.path])


def walk(m: h.Module, parents=tuple(), conns=dict()) -> Generator[PrimNode, None, None]:
    if not conns:
        conns = {**m.signals, **m.ports}
    for inst in m.instances.values():
        logger.debug(f"walk: {m.name} / {inst.name}")
        new_conns = {}
        new_parents = parents + (inst,)
        for src_port_name, sig in inst.conns.items():
            match sig:
                case h.Signal():
                    key = sig.name
                case h.PortRef():
                    key = sig.portname
                case _:
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
            yield PrimNode(inst, new_parents, new_conns)
        else:
            yield from walk(inst.of, new_parents, new_conns)


def _find_signal(m: h.Module, name: str) -> h.Signal:
    for port_name in m.ports:
        if port_name == name:
            return m.ports[port_name]
    for sig_name in m.signals:
        if sig_name == name:
            return m.signals[sig_name]
    raise ValueError(f"Signal {name} not found in module {m.name}")


def is_flat(m: h.Instance | h.Instantiable) -> bool:
    if isinstance(m, h.Instance):
        return is_flat(m.of)
    elif isinstance(m, (h.PrimitiveCall, h.GeneratorCall, h.ExternalModuleCall)):
        return True
    elif isinstance(m, h.Module):
        insts = m.instances.values()
        return all(isinstance(inst.of, h.PrimitiveCall) for inst in insts)
    else:
        raise ValueError(f"Unexpected type {type(m)}")


def flat_conns(conns):
    flat = tree.flatten_with_path(conns)
    return {":".join(reversed(path)): value.name for path, value in flat}


def flat_module(m: h.Module):
    m = h.elaborate(m)

    nodes = list(walk(m))
    for n in nodes:
        logger.debug(str(n))

    new_module = h.Module((m.name or "module") + "_flat")
    for port_name in m.ports:
        new_module.add(h.Port(name=port_name))

    for n in nodes:
        for sig in n.conns.values():
            sig_name = sig.name
            if sig_name not in new_module.ports:
                new_module.add(h.Signal(name=sig_name))

    for n in nodes:
        new_inst = new_module.add(n.inst.of(), name=n.make_name())

        for src_port_name, sig in n.conns.items():
            matching_sig = _find_signal(new_module, sig.name)
            new_inst.connect(src_port_name, matching_sig)

    return new_module
