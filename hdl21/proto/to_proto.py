"""
# VLSIR ProtoBuf Schema Export

Primary entrypoint `to_proto` turns a set of elaborate-able `Elaboratables`, 
and turns them into a `vlsir.circuit.Package`. 

Most export-machinery is accomplished by primary implementation-class `ProtoExporter`, 
which particularly handles hierarchically-referential types such as `Module`, `Instance`, and `ExternalModule`. 

Exports of simpler "scalar"(-ish) types such as `Signal`s and `Param`s are provided as 
free-standing functions to enable use elsewhere. 
"""

from decimal import Decimal
from textwrap import dedent
from dataclasses import fields
from enum import Enum
from typing import Optional, List, Union, Dict, Any

from pydantic.dataclasses import dataclass

# Local imports
# Proto-definitions
import vlsir
import vlsir.circuit_pb2 as vckt

# HDL
from ..params import isparamclass
from ..prefix import Prefix, Prefixed
from ..scalar import Scalar
from ..literal import Literal
from ..elab import Elaboratables, elaborate
from ..module import Module
from ..qualname import qualname as module_qualname
from ..external_module import ExternalModule, ExternalModuleCall
from ..instance import Instance
from ..signal import Signal, Port, PortDir
from ..slice import Slice
from ..concat import Concat
from ..primitives import (
    PrimitiveCall,
    PrimitiveType,
    PulseVoltageSourceParams,
)


def to_proto(
    top: Elaboratables,
    domain: Optional[str] = None,
    **kwargs,
) -> vckt.Package:
    """Convert Elaborate-able Module or Generator `top` and its dependencies to a Proto-format `Package`."""
    # Elaborate all the top-level Modules
    tops = elaborate(top)
    if not isinstance(tops, list):
        tops = [tops]
    exporter = ProtoExporter(tops=tops, domain=domain)
    return exporter.export()


@dataclass
class ModuleMapping:
    hmod: Module  # hdl21.Module
    pmod: vckt.Module  # VLSIR Module


class ProtoExporter:
    """
    Hierarchical Protobuf Exporter
    Walks a Module hierarchy from Module `self.top`, defining each required Module along the way.
    Modules are defined in `self.pkg` in dependency order.
    Upon round-tripping, all dependent child-modules will be encountered before their parent instantiators.
    """

    def __init__(self, tops: List[Module], domain: Optional[str] = None):
        self.tops = tops

        # Module mappings, keyed by (a) hdl21.Module (ID), and (b) vlsir.Module (name)
        self.modules_by_id: Dict[int, ModuleMapping] = dict()
        self.modules_by_name: Dict[str, ModuleMapping] = dict()

        # ExternalModule-id to Proto-ExternalModule dict
        self.ext_modules: Dict[int, vckt.ExternalModule] = dict()

        # Default `domain` AKA package-name is the empty string
        self.pkg = vckt.Package(domain=domain or "")

    def export(self) -> vckt.Package:
        """Export starting with every Module in `self.tops`,
        visiting every hierarchical node along the way.
        Returns our generated `Package` as a result."""
        if not isinstance(self.tops, list):
            raise TypeError
        for m in self.tops:
            if not isinstance(m, Module):
                raise TypeError
            self.export_module(m)
        return self.pkg

    def export_module_name(self, module: Module) -> vlsir.utils.QualifiedName:
        """Create and return a unique `QualifiedName` for Module `module`.
        Raises a `RuntimeError` if unique name is taken."""

        mname = module_qualname(module)
        if "Mos(7271d1c5009776529f754c575eb55012)" in mname:
            print(5)
        if mname in self.modules_by_name:
            conflict = self.modules_by_name[mname].hmod
            msg = f"Cannot serialize Module {module} due to conflicting name with {conflict}. \n"
            msg += "(Was this a generator that didn't get decorated with `@hdl21.generator`?) "
            raise RuntimeError(msg)
        return mname

    def export_module(self, module: Module) -> vckt.Module:
        """Export a Module `module` and all its dependencies."""

        if id(module) in self.modules_by_id:  # Already done
            return self.modules_by_id[id(module)].pmod

        if module.bundles:  # Can't handle these, at least for now
            msg = f"Invalid attribute for Proto export: Module {module.name} with Bundles {list(module.bundles.keys())}"
            raise RuntimeError(msg)

        # Create the Proto-Module
        pmod = vckt.Module()

        # Create its serialized name
        pmod.name = self.export_module_name(module)

        # Create its Signal-objects, which include the hdl21.Module's Ports
        for sig in list(module.signals.values()) + list(module.ports.values()):
            psig = vckt.Signal(name=sig.name, width=sig.width)
            pmod.signals.append(psig)

        # Create its Port-objects
        for port in module.ports.values():
            pmod.ports.append(export_port(port))

        # Create each Proto-Instance
        for inst in module.instances.values():
            if not inst._resolved:
                msg = f"Invalid Instance {inst.name} of unresolved Module in Module {module.name}"
                raise RuntimeError(msg)
            pinst = self.export_instance(inst)
            pmod.instances.append(pinst)

        # Store references to the result, and return it
        mapping = ModuleMapping(module, pmod)
        self.modules_by_id[id(module)] = mapping
        self.modules_by_name[pmod.name] = mapping
        self.pkg.modules.append(pmod)
        return pmod

    def export_external_module(self, emod: ExternalModule) -> vckt.ExternalModule:
        """Export an `ExternalModule`"""
        if id(emod) in self.ext_modules:  # Already done
            return self.ext_modules[id(emod)]

        # Create the Proto-ExternalModule
        qname = vlsir.utils.QualifiedName(name=emod.name, domain=emod.domain)
        pmod = vckt.ExternalModule(name=qname)

        # Create its Port-objects, which also require Vlsir Signal objects
        for port in emod.port_list:
            psig = vckt.Signal(name=port.name, width=port.width)
            pmod.signals.append(psig)
            pmod.ports.append(export_port(port))

        # Store references to the result, and return it
        self.ext_modules[id(emod)] = pmod
        self.pkg.ext_modules.append(pmod)
        return pmod

    def export_instance(self, inst: Instance) -> vckt.Instance:
        """Convert an hdl21.Instance into a Proto-Instance
        Depth-first retrieves a Module definition first,
        using its generated `name` field as the Instance's `module` pointer."""

        # Create the Proto-Instance
        pinst = vckt.Instance(name=inst.name)

        # First depth-first seek out our definition,
        # Retrieving the data we need to make a `Reference` to it
        if isinstance(inst._resolved, Module):
            pmod = self.export_module(inst._resolved)
            # Give it a Reference to its Module
            pinst.module.local = pmod.name
        elif isinstance(inst._resolved, (PrimitiveCall, ExternalModuleCall)):
            call = inst._resolved

            if isinstance(inst._resolved, PrimitiveCall):
                # Create a reference to one of the `primitive` namespaces
                if call.prim.primtype == PrimitiveType.PHYSICAL:
                    # FIXME: #54 also expose the `hdl21.primitives` as a VLSIR package
                    pinst.module.external.domain = "hdl21.primitives"
                    pinst.module.external.name = call.prim.name
                    params = dictify_params(call.params)
                elif call.prim.primtype == PrimitiveType.IDEAL:
                    # Ideal elements convert to `vlsir.primitives`
                    pinst.module.external.domain = "vlsir.primitives"
                    prim_map = {
                        "DcVoltageSource": "vdc",
                        "PulseVoltageSource": "vpulse",
                        "SineVoltageSource": "vsin",
                        "CurrentSource": "isource",
                        "IdealResistor": "resistor",
                        "IdealCapacitor": "capacitor",
                        "IdealInductor": "inductor",
                        "VoltageControlledVoltageSource": "vcvs",
                        "CurrentControlledVoltageSource": "ccvs",
                        "VoltageControlledCurrentSource": "vccs",
                        "CurrentControlledCurrentSource": "cccs",
                    }
                    if call.prim.name not in prim_map:
                        msg = f"Invalid Primitive {call.prim.name} in PrimitiveCall {inst.name}"
                        raise RuntimeError(msg)
                    pinst.module.external.name = prim_map[call.prim.name]
                    params = export_primitive_params(call.params)
                else:
                    raise ValueError(f"Invalid PrimitiveType {call.prim.primtype}")

            elif isinstance(inst._resolved, ExternalModuleCall):
                self.export_external_module(call.module)
                pinst.module.external.domain = call.module.domain or ""
                pinst.module.external.name = call.module.name
                params = dictify_params(call.params)

            else:
                msg = f"Un-exportable Instance {inst} resolves to invalid type {inst._resolved}"
                raise TypeError(msg)

            # Export the instance parameters
            for key, val in params.items():
                if val is None:
                    continue  # None-valued parameters go un-set
                # Otherwise export and copy it into place
                vparam = vlsir.Param(name=key, value=export_param_value(val))
                pinst.parameters.append(vparam)

        else:
            raise TypeError(f"Un-exportable Instance {inst} of {inst._resolved}")

        # Create its connections mapping
        for pname, conn in inst.conns.items():
            # Assign each item into the connections dict.
            # The proto interface requires copying it along the way
            pconn = vckt.Connection(
                portname=pname, target=export_connection_target(conn)
            )
            pinst.connections.append(pconn)

        return pinst


def export_port(port: Port) -> vckt.Port:
    """Export a `Port`"""
    pport = vckt.Port()
    pport.direction = export_port_dir(port)
    pport.signal = port.name
    return pport


def export_port_dir(port: Port) -> vckt.Port.Direction:
    """Convert between Port-Direction Enumerations"""
    if port.direction == PortDir.INPUT:
        return vckt.Port.Direction.INPUT
    if port.direction == PortDir.OUTPUT:
        return vckt.Port.Direction.OUTPUT
    if port.direction == PortDir.INOUT:
        return vckt.Port.Direction.INOUT
    if port.direction == PortDir.NONE:
        return vckt.Port.Direction.NONE
    raise ValueError(f"Invalid PortDir {port.direction}")


def export_connection_target(
    sig: Union[Signal, Slice, Concat]
) -> vckt.ConnectionTarget:
    """Export a proto `ConnectionTarget`"""

    pconn = vckt.ConnectionTarget()  # Create a proto-Connection
    if isinstance(sig, Signal):
        pconn.sig = sig.name
    elif isinstance(sig, Slice):
        pslice = export_slice(sig)
        pconn.slice.CopyFrom(pslice)
    elif isinstance(sig, Concat):
        pconc = export_concat(sig)
        pconn.concat.CopyFrom(pconc)
    else:
        msg = f"Invalid argument to `export_connection_target`: {sig}"
        raise TypeError(msg)
    return pconn


def export_slice(slize: Slice) -> vckt.Slice:
    """Export a signal-`Slice`.
    Fails if the parent is not a concrete `Signal`, i.e. it is a `Concat` or another `Slice`.
    Fails for non-unit step-sizes, which should be converted to `Concat`s upstream."""
    if not isinstance(slize.parent, Signal):
        msg = f"Export error: {slize} has a parent {slize.parent} which is not a concrete Signal"
        raise RuntimeError(msg)
    if slize.step != 1:
        msg = f"Export error: {slize} has non-unit step"
        raise RuntimeError(msg)

    # Move to HDL-style indexing, with inclusive `top` index.
    return vckt.Slice(signal=slize.parent.name, top=slize.top - 1, bot=slize.bot)


def export_concat(concat: Concat) -> vckt.Concat:
    """Export (potentially recursive) Signal Concatenations"""
    pconc = vckt.Concat()
    for part in concat.parts:
        pconc.parts.append(export_connection_target(part))
    return pconc


def export_primitive_params(params: Any) -> Dict[str, Optional[Prefixed]]:
    """Convert the parameters of an `IDEAL` primitive into their VLSIR form.
    Returns the result as a dictionary of {name: value}s."""

    if isinstance(params, PulseVoltageSourceParams):
        return dict(
            v1=params.v1,
            v2=params.v2,
            td=params.delay,
            tr=params.rise,
            tf=params.fall,
            tpw=params.width,
            tper=params.period,
        )

    # For everything else, pass along the values name-by-name as a dictionary.
    return dictify_params(params)


def dictify_params(params: Any) -> Dict[str, Optional[Prefixed]]:
    """Turn a `paramclass` of parameters into a dictionary of exportable values.
    This is essentially a one-layer replacement for the standard library's
    `dataclasses.as_dict`, which we replace for sake of our "near-scalar" types
    such as `Prefixed` numbers."""

    if isinstance(params, dict):
        return params

    if not isparamclass(params):
        msg = f"Invalid Parameter Call-Argument {params} - must be either `dict` or `hdl21.paramclass`"
        raise TypeError(msg)

    # And turn its fields into a dictionary
    return {field.name: getattr(params, field.name) for field in fields(params)}


# Alias for the union of (python) types which can be converted to Vlsir's `ParamValue`.
# These can generally be summarized as "numbers, strings, and things easily convertible into them".
# Hdl21 parameters can of course be a much larger set of types.
# Anything outside this list produces a `TypeError` when exported.
ToVlsirParam = Union[
    type(None), int, float, str, Decimal, Enum, Prefixed, Scalar, Literal
]


def export_param_value(val: ToVlsirParam) -> Optional[vlsir.ParamValue]:
    """Export a `ParamValue`."""

    if isinstance(val, type(None)):
        return None  # `None` serves as the null identifier for "no value".

    if isinstance(val, str):
        # FIXME: the debate between `string` and `literal`. For now, we use LITERAL.
        return vlsir.ParamValue(literal=val)
    # Enum-valued parameters must also be strings, or fail
    if isinstance(val, Enum):
        if not isinstance(val.value, str):
            raise TypeError(f"Enum-valued parameters must be strings, not {val.value}")
        return vlsir.ParamValue(literal=val.value)

    # Internal numeric (and number-like) types
    if isinstance(val, Scalar):
        # `Scalar` will either have an internal `Literal` or `Prefixed` value.
        val = val.inner
    if isinstance(val, Literal):  # String/ expression literals
        return vlsir.ParamValue(literal=val.txt)
    if isinstance(val, Prefixed):
        return vlsir.ParamValue(prefixed=export_prefixed(val))

    # Standard-Lib Numbers
    if isinstance(val, Decimal):
        return vlsir.ParamValue(literal=str(val))
    if isinstance(val, int):
        return vlsir.ParamValue(integer=val)
    if isinstance(val, float):
        return vlsir.ParamValue(double=val)

    msg = f"Unsupported parameter for proto-export: `{val}`"
    raise TypeError(msg)


def export_prefix(pre: Prefix) -> vlsir.SIPrefix:
    """Export an enumerated `Prefix`"""
    map = {
        -24: vlsir.SIPrefix.YOCTO,
        -21: vlsir.SIPrefix.ZEPTO,
        -18: vlsir.SIPrefix.ATTO,
        -15: vlsir.SIPrefix.FEMTO,
        -12: vlsir.SIPrefix.PICO,
        -9: vlsir.SIPrefix.NANO,
        -6: vlsir.SIPrefix.MICRO,
        -3: vlsir.SIPrefix.MILLI,
        -2: vlsir.SIPrefix.CENTI,
        -1: vlsir.SIPrefix.DECI,
        0: vlsir.SIPrefix.UNIT,
        1: vlsir.SIPrefix.DECA,
        2: vlsir.SIPrefix.HECTO,
        3: vlsir.SIPrefix.KILO,
        6: vlsir.SIPrefix.MEGA,
        9: vlsir.SIPrefix.GIGA,
        12: vlsir.SIPrefix.TERA,
        15: vlsir.SIPrefix.PETA,
        18: vlsir.SIPrefix.EXA,
        21: vlsir.SIPrefix.ZETTA,
        24: vlsir.SIPrefix.YOTTA,
    }
    if pre.value not in map:
        raise ValueError(f"Invalid Prefix {pre}")
    return map[pre.value]


def export_prefixed(pref: Prefixed) -> vlsir.Prefixed:
    """Export a `Prefixed` number"""

    # Export the metric prefix
    prefix = export_prefix(pref.prefix)

    # And export the numeric part. Use Vlsir's `integer` variant for Decimal values which equal integers, and strings otherwise.
    if pref.number == int(pref.number):
        return vlsir.Prefixed(integer=int(pref.number), prefix=prefix)
    return vlsir.Prefixed(string=str(pref.number), prefix=prefix)


# FIXME: #54 also expose the `hdl21.primitives` as a VLSIR package
# @classmethod
# def export_hdl21_primitive(cls, prim: Primitive) -> vckt.ExternalModule:
#     """ Export a `Primitive` as a `vckt.ExternalModule`.
#     Not typically done as part of serialization,
#     but solely as an aid to other conversion utilities. """
#
#     # Create the Proto-ExternalModule
#     if prim.primtype == PrimitiveType.PHYSICAL:
#         domain = "hdl21.primitives"
#     elif prim.primtype == PrimitiveType.IDEAL:
#         domain = "hdl21.ideal"
#     else:
#         raise ValueError
#     qname = vlsir.utils.QualifiedName(name=prim.name, domain=domain)
#     pmod = vckt.ExternalModule(name=qname)
#
#     # Create its Port-objects
#     for port in prim.port_list:
#         pmod.ports.append(cls.export_port(port))
#
#     # And return it
#     return pmod
