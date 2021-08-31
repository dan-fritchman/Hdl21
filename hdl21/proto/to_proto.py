"""
hdl21 ProtoBuf Export
"""

from textwrap import dedent
from dataclasses import asdict, is_dataclass
from enum import Enum
from types import SimpleNamespace
from typing import Optional, List, Union

# Local imports
# Proto-definitions
from . import circuit_pb2 as protodefs

# HDL
from ..elab import Elabables, elab_all
from ..module import Module, ExternalModule, ExternalModuleCall
from ..primitives import Primitive, PrimitiveCall, PrimitiveType
from ..instance import Instance
from .. import signal


def to_proto(
    top: Elabables, domain: Optional[str] = None, **kwargs,
) -> protodefs.Package:
    """Convert Elaborate-able Module or Generator `top` and its dependencies to a Proto-format `Package`"""
    # Elaborate all the top-level Modules
    tops = elab_all(top)
    exporter = ProtoExporter(tops=tops, domain=domain)
    return exporter.export()


class ProtoExporter:
    """Hierarchical Protobuf Exporter.
    Walks a Module hierarchy from Module `self.top`, defining each required Module along the way.
    Modules are defined in `self.pkg` in dependency order.
    Upon round-tripping, all dependent child-modules will be encountered before their parent instantiators."""

    def __init__(self, tops: List[Module], domain: Optional[str] = None):
        self.tops = tops
        self.modules = dict()  # Module-id to Proto-Module dict
        self.module_names = dict()  # (Serialized) Module-name to Proto-Module dict
        self.ext_modules = dict()  # ExternalModule-id to Proto-ExternalModule dict
        # Default `domain` AKA package-name is the empty string
        self.pkg = protodefs.Package(domain=domain or "")

    def export(self) -> protodefs.Package:
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

    def export_module_name(self, module: Module) -> protodefs.QualifiedName:
        """Create and return a unique `QualifiedName` for Module `module`.
        Raises a `RuntimeError` if unique name is taken."""

        mname = module._qualname()
        if mname in self.module_names:
            conflict = self.module_names[mname]
            raise RuntimeError(
                dedent(
                    f"""\
                    Cannot serialize Module {module} due to conflicting name with {conflict}. 
                    (Was this a generator that didn't get decorated with `@hdl21.generator`?) """
                )
            )
        return mname

    def export_module(self, module: Module) -> protodefs.Module:
        if id(module) in self.modules:  # Already done
            return self.modules[id(module)]

        if module.interfaces:  # Can't handle these, at least for now
            raise RuntimeError(
                f"Invalid attribute for Proto export: Module {module.name} with Interfaces {list(module.interfaces.keys())}"
            )

        # Create the Proto-Module
        pmod = protodefs.Module()

        # Create its serialized name
        pmod.name = self.export_module_name(module)

        # Create its Port-objects
        for port in module.ports.values():
            pmod.ports.append(self.export_port(port))

        # Create its Signal-objects
        for sig in module.signals.values():
            psig = protodefs.Signal(name=sig.name, width=sig.width)
            pmod.signals.append(psig)

        # Create each Proto-Instance
        for inst in module.instances.values():
            if not inst._resolved:
                raise RuntimeError(
                    f"Invalid Instance {inst.name} of unresolved Module in Module {module.name}"
                )
            pinst = self.export_instance(inst)
            pmod.instances.append(pinst)

        # Store references to the result, and return it
        self.modules[id(module)] = pmod
        self.module_names[pmod.name] = pmod
        self.pkg.modules.append(pmod)
        return pmod

    def export_external_module(self, emod: ExternalModule) -> protodefs.ExternalModule:
        """Export an `ExternalModule`"""
        if id(emod) in self.ext_modules:  # Already done
            return self.ext_modules[id(emod)]

        # Create the Proto-ExternalModule
        qname = protodefs.QualifiedName(name=emod.name, domain=emod.domain)
        pmod = protodefs.ExternalModule(name=qname)

        # Create its Port-objects
        for port in emod.ports.values():
            pmod.ports.append(self.export_port(port))

        # Store references to the result, and return it
        self.ext_modules[id(emod)] = pmod
        self.pkg.ext_modules.append(pmod)
        return pmod

    @classmethod
    def export_primitive(cls, prim: Primitive) -> protodefs.ExternalModule:
        """Export a `Primitive as a `protodefs.ExternalModule`. 
        Not typically done as part of serialization, 
        but solely as an aid to other conversion utilities. """

        # Create the Proto-ExternalModule
        if prim.primtype == PrimitiveType.PHYSICAL:
            domain = "hdl21.primitives"
        elif prim.primtype == PrimitiveType.IDEAL:
            domain = "hdl21.ideal"
        else:
            raise ValueError
        qname = protodefs.QualifiedName(name=prim.name, domain=domain)
        pmod = protodefs.ExternalModule(name=qname)

        # Create its Port-objects
        for port in prim.port_list:
            pmod.ports.append(cls.export_port(port))

        # And return it
        return pmod

    @classmethod
    def export_port(cls, port: signal.Port) -> protodefs.Port:
        pport = protodefs.Port()
        pport.direction = cls.export_port_dir(port)
        pport.signal.name = port.name
        pport.signal.width = port.width
        return pport

    @classmethod
    def export_port_dir(cls, port: signal.Port) -> protodefs.Port.Direction:
        # Convert between Port-Direction Enumerations
        if port.direction == signal.PortDir.INPUT:
            return protodefs.Port.Direction.INPUT
        if port.direction == signal.PortDir.OUTPUT:
            return protodefs.Port.Direction.OUTPUT
        if port.direction == signal.PortDir.INOUT:
            return protodefs.Port.Direction.INOUT
        if port.direction == signal.PortDir.NONE:
            return protodefs.Port.Direction.NONE
        raise ValueError

    def export_instance(self, inst: Instance) -> protodefs.Instance:
        """Convert an hdl21.Instance into a Proto-Instance
        Depth-first retrieves a Module definition first,
        using its generated `name` field as the Instance's `module` pointer."""

        # Create the Proto-Instance
        pinst = protodefs.Instance(name=inst.name)

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
                    pinst.module.external.domain = "hdl21.primitives"
                elif call.prim.primtype == PrimitiveType.IDEAL:
                    pinst.module.external.domain = "hdl21.ideal"
                else:
                    raise ValueError
                pinst.module.external.name = call.prim.name
                params = asdict(call.params)
            else:  # ExternalModuleCall
                self.export_external_module(call.module)
                pinst.module.external.domain = call.module.domain or ""
                pinst.module.external.name = call.module.name
                # FIXME: while these ExternalModule parameters can ostensibly be anything,
                # there are really two supported types-of-types:
                # dictionaries, and dataclasses (which we can turn into dictionaries)
                if isinstance(call.params, dict):
                    params = call.params
                elif is_dataclass(call.params):
                    params = asdict(call.params)
                else:
                    raise TypeError

            # Set the parameter-values
            for key, val in params.items():
                if isinstance(val, type(None)):
                    continue  # None-valued parameters go un-set
                elif isinstance(val, int):
                    pinst.parameters[key].integer = val
                elif isinstance(val, float):
                    pinst.parameters[key].double = val
                elif isinstance(val, str):
                    pinst.parameters[key].string = val
                elif isinstance(val, Enum):
                    # Enum-valued parameters are always strings
                    pinst.parameters[key].string = val.value
                else:
                    raise TypeError(f"Invalid instance parameter {val} for {inst}")
        else:
            raise TypeError

        # Create its connections mapping
        for pname, sig in inst.conns.items():
            # Create a proto-Connection
            pconn = protodefs.Connection()

            if isinstance(sig, signal.Signal):
                pconn.sig.name = sig.name
                pconn.sig.width = sig.width
            elif isinstance(sig, signal.Slice):
                pconn.slice.signal = sig.signal.name
                pconn.slice.bot = sig.bot
                pconn.slice.top = sig.top
            elif isinstance(sig, signal.Concat):
                pconc = self.export_concat(sig)
                pconn.concat.CopyFrom(pconc)
            else:
                raise TypeError
            # Assign it into the connections dict.
            # The proto interface requires copying it along the way
            pinst.connections[pname].CopyFrom(pconn)

        return pinst

    def export_concat(self, concat: signal.Concat) -> protodefs.Concat:
        """Export (potentially recursive) Signal Concatenations"""
        pconc = protodefs.Concat()
        for part in concat.parts:
            if isinstance(part, signal.Signal):
                psig = protodefs.Signal(name=part.name, width=part.width)
                pconn = protodefs.Connection()
                pconn.sig.CopyFrom(psig)
                pconc.parts.append(pconn)
            elif isinstance(part, signal.Slice):
                psig = protodefs.Slice(
                    signal=part.signal.name, top=part.top, bot=part.bot
                )
                pconn = protodefs.Connection()
                pconn.slice.CopyFrom(psig)
                pconc.parts.append(pconn)
            elif isinstance(part, signal.Concat):
                sub_pconc = self.export_concat(part)
                pconn = protodefs.Connection()
                pconn.concat.CopyFrom(sub_pconc)
                pconc.parts.append(pconn)
            else:
                raise TypeError
        return pconc
