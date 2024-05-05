#!/usr/bin/env python3
#
# Exports PDK data in Vlsir schema format (protobufs).

# To run this without installation (maybe during development), you need to
# specify paths to VlsirTools, the Vlsir proto bindings, Hdl21 and the Sky130
# PDK package (this one):
#   PYTHONPATH=/path/Hdl21/pdks/Sky130:/path/Hdl21:/path/Vlsir/VlsirTools/:/path/Vlsir/bindings/python/ \
#   ./export.py --text_format

from collections.abc import Sequence
from typing import Optional, Dict

import optparse

import google.protobuf.text_format as text_format
import vlsir.circuit_pb2 as vlsir_circuit
import hdl21 as h

from sky130_hdl21 import pdk_data
from sky130_hdl21.primitives import prim_dicts
from tabulate import tabulate


def define_options(optparser: optparse.OptionParser):
    optparser.add_option(
        "-o",
        "--output",
        dest="output",
        default="sky130.primitives.pb",
        help="name of proto file to export to",
    )
    optparser.add_option(
        "-t",
        "--text_format",
        dest="text_format",
        action="store_true",
        default=False,
        help="also export text format version of protobuf",
    )


def collect_other_primitives(
    defs: Dict[str, h.ExternalModule], modules: [h.ExternalModule]
):
    table_rows = []
    for name, module in prim_dicts.ress.items():
        table_rows.append([name, module.name])
        modules.append(module)
    print(tabulate(table_rows))


def process(options: optparse.Values):
    # The primitives are conveniently listed in sky130_hdl21.prim_dicts. You
    # could also scrape sky130_hdl21.primitives.__dict__, but don't.
    ext_modules: [h.ExternalModule] = []

    print("Transistors:")
    table_rows = []
    for mos_key, module in prim_dicts.xtors.items():
        name, mos_type, mos_vth, mos_family = mos_key
        table_rows.append([name, module.name, mos_type, mos_vth, mos_family])
        ext_modules.append(module)
    print(tabulate(table_rows))

    others = {
        "Resistors": prim_dicts.ress,
        "Diodes": prim_dicts.diodes,
        "BJTs": prim_dicts.bjts,
        "VPPs": prim_dicts.vpps,
    }

    for name, defs in others.items():
        print(f"{name}:")
        collect_other_primitives(defs, ext_modules)

    package_pb = vlsir_circuit.Package()
    package_pb.domain = pdk_data.PDK_NAME

    for module in ext_modules:
        module_pb = h.proto.exporting.export_external_module(module)
        for name, param in module.paramtype.__params__.items():
            param_pb = module_pb.parameters.add()
            param_pb.name = name
            param_pb.value.CopyFrom(h.proto.exporting.export_param_value(param.default))
            param_pb.desc = param.desc

        package_pb.ext_modules.append(module_pb)

    print(f"\nwriting {options.output}")
    with open(f"{options.output}", "wb") as f:
        f.write(package_pb.SerializeToString())

    if options.text_format:
        filename = f"{options.output}.txt"
        print(f"writing {filename}")
        with open(filename, "w") as f:
            f.write(text_format.MessageToString(package_pb))


def main():
    optparser = optparse.OptionParser()
    define_options(optparser)
    options, _ = optparser.parse_args()
    process(options)


if __name__ == "__main__":
    main()
