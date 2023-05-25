from dataclasses import replace
from enum import Enum
from typing import Any

import pytest

import hdl21 as h
from hdl21.flatten import flatten, is_flat, walk


@h.module
class Inverter:
    vdd, vss, vin, vout = h.Ports(4)
    pmos = h.Pmos()(d=vout, g=vin, s=vdd, b=vdd)
    nmos = h.Nmos()(d=vout, g=vin, s=vss, b=vss)


@h.module
class Buffer:
    vdd, vss, vin, vout = h.Ports(4)
    inv_1 = Inverter(vdd=vdd, vss=vss, vin=vin)  # type: ignore
    inv_2 = Inverter(vdd=vdd, vss=vss, vin=inv_1.vout, vout=vout)  # type: ignore


@h.module
class DoubleBuffer:
    vdd, vss, vin, vout = h.Ports(4)
    buffer_1 = Buffer(vdd=vdd, vss=vss, vin=vin)
    buffer_2 = Buffer(vdd=vdd, vss=vss, vin=buffer_1.vout, vout=vout)


@h.module
class InvBuffer:
    vdd, vss, vin, vout = h.Ports(4)
    inv = Inverter(vdd=vdd, vss=vss, vin=vin)
    buffer = Buffer(vdd=vdd, vss=vss, vin=inv.vout, vout=vout)


def test_is_flat():
    assert is_flat(Inverter)
    assert not is_flat(Buffer)
    assert not is_flat(InvBuffer)


def test_flatten_inv():
    inv = Inverter
    assert is_flat(inv)
    inv_raw_proto = h.to_proto(h.elaborate(inv))
    inv_flatten_proto = h.to_proto(flatten(inv))
    assert inv_raw_proto == inv_flatten_proto


def test_flatten_buffer():
    buffer = Buffer
    assert not is_flat(buffer)
    buffer_flat = flatten(buffer)
    assert buffer_flat.instances.keys() == {
        "inv_1:pmos",
        "inv_1:nmos",
        "inv_2:pmos",
        "inv_2:nmos",
    }
    assert buffer_flat.ports.keys() == {"vdd", "vss", "vin", "vout"}
    assert buffer_flat.signals.keys() == {"inv_1_vout"}
    assert is_flat(buffer_flat)


def test_flatten_double_buffer():
    double_buffer = DoubleBuffer
    assert not is_flat(double_buffer)
    double_buffer_flat = flatten(double_buffer)
    assert double_buffer_flat.instances.keys() == {
        "buffer_1:inv_1:pmos",
        "buffer_1:inv_1:nmos",
        "buffer_1:inv_2:pmos",
        "buffer_1:inv_2:nmos",
        "buffer_2:inv_1:pmos",
        "buffer_2:inv_1:nmos",
        "buffer_2:inv_2:pmos",
        "buffer_2:inv_2:nmos",
    }
    assert double_buffer_flat.ports.keys() == {"vdd", "vss", "vin", "vout"}
    assert double_buffer_flat.signals.keys() == {
        "buffer_1_vout",  # connection between two buffers
        "buffer_1:inv_1_vout",  # internal signal between two inverters in buffer 1
        "buffer_2:inv_1_vout",  # internal signal between two inverters in buffer 2
    }
    assert is_flat(double_buffer_flat)


def test_flatten_inv_buffer():
    inv_buffer = InvBuffer
    assert not is_flat(inv_buffer)
    inv_buffer_flat = flatten(inv_buffer)
    assert inv_buffer_flat.instances.keys() == {
        "inv:pmos",
        "inv:nmos",
        "buffer:inv_1:pmos",
        "buffer:inv_1:nmos",
        "buffer:inv_2:pmos",
        "buffer:inv_2:nmos",
    }
    assert inv_buffer_flat.ports.keys() == {"vdd", "vss", "vin", "vout"}
    assert inv_buffer_flat.signals.keys() == {"inv_vout", "buffer:inv_1_vout"}
    assert is_flat(inv_buffer_flat)


def test_flatten_node_desc():
    nodes = list(walk(Buffer))
    assert (
        str(nodes[0])
        == "{'name': 'inv_1:pmos', 'path': ['inv_1', 'pmos'], 'conns': {'d': 'inv_1_vout', 'g': 'vin', 's': 'vdd', 'b': 'vdd'}}"
    )
