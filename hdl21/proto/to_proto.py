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
import vlsir

# HDL
from ..elab import Elabables, elab_all
from ..module import Module, ExternalModule, ExternalModuleCall
from ..primitives import Primitive, PrimitiveCall, PrimitiveType
from ..instance import Instance
from .. import signal


def to_proto(
    top: Elabables, domain: Optional[str] = None, **kwargs,
) -> vlsir.circuit.Package:
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
        self.pkg = vlsir.circuit.Package(domain=domain or "")

    def export(self) -> vlsir.circuit.Package:
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

    def export_module(self, module: Module) -> vlsir.circuit.Module:
        if id(module) in self.modules:  # Already done
            return self.modules[id(module)]

        if module.bundles:  # Can't handle these, at least for now
            raise RuntimeError(
                f"Invalid attribute for Proto export: Module {module.name} with Bundles {list(module.bundles.keys())}"
            )

        # Create the Proto-Module
        pmod = vlsir.circuit.Module()

        # Create its serialized name
        pmod.name = self.export_module_name(module)

        # Create its Port-objects
        for port in module.ports.values():
            pmod.ports.append(self.export_port(port))

        # Create its Signal-objects
        for sig in module.signals.values():
            psig = vlsir.circuit.Signal(name=sig.name, width=sig.width)
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

    def export_external_module(
        self, emod: ExternalModule
    ) -> vlsir.circuit.ExternalModule:
        """ Export an `ExternalModule` """
        if id(emod) in self.ext_modules:  # Already done
            return self.ext_modules[id(emod)]

        # Create the Proto-ExternalModule
        qname = vlsir.utils.QualifiedName(name=emod.name, domain=emod.domain)
        pmod = vlsir.circuit.ExternalModule(name=qname)

        # Create its Port-objects
        for port in emod.ports.values():
            pmod.ports.append(self.export_port(port))

        # Store references to the result, and return it
        self.ext_modules[id(emod)] = pmod
        self.pkg.ext_modules.append(pmod)
        return pmod

    @classmethod
    def export_hdl21_primitive(cls, prim: Primitive) -> vlsir.circuit.ExternalModule:
        """ Export a `Primitive` as a `vlsir.circuit.ExternalModule`. 
        Not typically done as part of serialization, 
        but solely as an aid to other conversion utilities. """

        # Create the Proto-ExternalModule
        if prim.primtype == PrimitiveType.PHYSICAL:
            domain = "hdl21.primitives"
        elif prim.primtype == PrimitiveType.IDEAL:
            domain = "hdl21.ideal"
        else:
            raise ValueError
        qname = vlsir.utils.QualifiedName(name=prim.name, domain=domain)
        pmod = vlsir.circuit.ExternalModule(name=qname)

        # Create its Port-objects
        for port in prim.port_list:
            pmod.ports.append(cls.export_port(port))

        # And return it
        return pmod

    @classmethod
    def export_port(cls, port: signal.Port) -> vlsir.circuit.Port:
        pport = vlsir.circuit.Port()
        pport.direction = cls.export_port_dir(port)
        pport.signal.name = port.name
        pport.signal.width = port.width
        return pport

    @classmethod
    def export_port_dir(cls, port: signal.Port) -> vlsir.circuit.Port.Direction:
        # Convert between Port-Direction Enumerations
        if port.direction == signal.PortDir.INPUT:
            return vlsir.circuit.Port.Direction.INPUT
        if port.direction == signal.PortDir.OUTPUT:
            return vlsir.circuit.Port.Direction.OUTPUT
        if port.direction == signal.PortDir.INOUT:
            return vlsir.circuit.Port.Direction.INOUT
        if port.direction == signal.PortDir.NONE:
            return vlsir.circuit.Port.Direction.NONE
        raise ValueError

    def export_instance(self, inst: Instance) -> vlsir.circuit.Instance:
        """ Convert an hdl21.Instance into a Proto-Instance
        Depth-first retrieves a Module definition first,
        using its generated `name` field as the Instance's `module` pointer. """

        # Create the Proto-Instance
        pinst = vlsir.circuit.Instance(name=inst.name)

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
                    pinst.module.external.name = call.prim.name
                elif call.prim.primtype == PrimitiveType.IDEAL:
                    # Ideal elements convert to `vlsir.primitives`
                    pinst.module.external.domain = "vlsir.primitives"
                    prim_map = {
                        "DcVoltageSource": "vdc",
                        "IdealCurrentSource": "isource",
                        "IdealResistor": "resistor",
                        "IdealCapacitor": "capacitor",
                        "IdealInductor": "inductor",
                    }
                    if call.prim.name not in prim_map:
                        msg = f"Invalid Primitive {call.prim.name} in PrimitiveCall {inst.name}"
                        raise RuntimeError(msg)
                    # Set the
                    pinst.module.external.name = prim_map[call.prim.name]
                else:
                    raise ValueError
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
                    msg = f"Invalid ExternalModule parameter-type for export: {call.params}"
                    raise TypeError(msg)

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
            # Assign each item into the connections dict.
            # The proto interface requires copying it along the way
            pinst.connections[pname].CopyFrom(self.export_conn(sig))

        return pinst

    def export_conn(
        self, sig: Union[signal.Signal, signal.Slice, signal.Concat]
    ) -> vlsir.circuit.Connection:
        """ Export a proto Connection """

        pconn = vlsir.circuit.Connection()  # Create a proto-Connection
        if isinstance(sig, signal.Signal):
            pconn.sig.name = sig.name
            pconn.sig.width = sig.width
        elif isinstance(sig, signal.Slice):
            pslice = self.export_slice(sig)
            pconn.slice.CopyFrom(pslice)
        elif isinstance(sig, signal.Concat):
            pconc = self.export_concat(sig)
            pconn.concat.CopyFrom(pconc)
        else:
            raise TypeError(f"Invalid argument to `ProtoExporter.export_conn`: {sig}")
        return pconn

    def export_slice(self, slize: signal.Slice) -> vlsir.circuit.Slice:
        """ Export a signal-`Slice`. 
        Fails if the parent is not a concrete `Signal`, i.e. it is a `Concat` or another `Slice`. 
        Fails for non-unit step-sizes, which should be converted to `Concat`s upstream. """
        if not isinstance(slize.signal, signal.Signal):
            msg = f"Export error: {slize} has a parent {slize.signal} which is not a concrete Signal"
            raise RuntimeError(msg)
        if slize.step is not None and slize.step != 1:
            msg = f"Export error: {slize} has non-unit step"
            raise RuntimeError(msg)

        # Move to HDL-style indexing, with inclusive `top` index.
        return vlsir.circuit.Slice(
            signal=slize.signal.name, top=slize.top - 1, bot=slize.bot
        )

    def export_concat(self, concat: signal.Concat) -> vlsir.circuit.Concat:
        """ Export (potentially recursive) Signal Concatenations """
        pconc = vlsir.circuit.Concat()
        for part in concat.parts:
            pconc.parts.append(self.export_conn(part))
        return pconc
