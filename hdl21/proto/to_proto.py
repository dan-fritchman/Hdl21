"""
hdl21 ProtoBuf Export
"""

# Local imports
# Proto-definitions
from . import circuit_pb2 as protodefs

# HDL
from ..elab import elaborate, Elabable
from ..module import Module
from ..instance import Instance
from .. import signal


def to_proto(top: Elabable, **kwargs) -> protodefs.Package:
    """ Convert Elaborate-able Module or Generator `top` and its dependencies to a Proto-format `Package` """
    top = elaborate(top=top, **kwargs)
    exporter = ProtoExporter(top=top)
    return exporter.export()


class ProtoExporter:
    """ Hierarchical Protobuf Exporter. 
    Walks a Module hierarchy from Module `self.top`, defining each required Module along the way. 
    Modules are defined in `self.pkg` in dependency order. 
    Upon round-tripping, all dependent child-modules will be encountered before their parent instantiators. """

    def __init__(self, top: Module):
        self.top = top
        self.modules = dict()  # Module-id to Proto-Module dict
        self.pkg = protodefs.Package(name="THIS_LIBRARY")

    def export(self) -> protodefs.Package:
        """ Export starting at `self.top`, visiting every hierarchical node along the way. 
        Returns our generated `Package` as a result. """
        if not isinstance(self.top, Module):
            raise TypeError
        self.export_module(self.top)
        return self.pkg

    def export_module(self, module: Module) -> protodefs.Module:
        if id(module) in self.modules:  # Already done
            return self.modules[id(module)]

        if module.interfaces:  # Can't handle these, at least for now
            raise RuntimeError(
                f"Invalid attribute for Proto export: Module {module.name} with Interfaces {list(module.interfaces.keys())}"
            )

        # Create the Proto-Module
        pmod = protodefs.Module()

        # FIXME: unique naming
        pmod.name.domain = "THIS_LIBRARYS_FLAT_NAMESPACE"
        pmod.name.name = module.name

        # Create its Port-objects
        for port in module.ports.values():
            pport = protodefs.Port()
            pport.direction = self.export_port_dir(port)
            pport.signal.name = port.name
            pport.signal.width = port.width
            pmod.ports.append(pport)

        # Create its Signal-objects
        for sig in module.signals.values():
            psig = protodefs.Signal(name=sig.name, width=sig.width)
            pmod.signals.append(psig)

        # Create each Proto-Instance
        for inst in module.instances.values():
            if not inst.module:
                raise RuntimeError(
                    f"Invalid Instance {inst.name} of unresolved Module in Module {module.name}"
                )
            pinst = self.export_instance(inst)
            pmod.instances.append(pinst)

        # Store a reference to the result, and return it
        self.modules[id(module)] = pmod
        self.pkg.modules.append(pmod)
        return pmod

    def export_port_dir(self, port: signal.Port) -> protodefs.Port.Direction:
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
        """ Convert an hdl21.Instance into a Proto-Instance 
        Depth-first retrieves a Module definition first, 
        using its generated `name` field as the Instance's `module` pointer. """

        # First depth-first seek out our definition,
        # Retrieving the data we need to make a `Reference` to it
        pmod = self.export_module(inst.module)

        # Create the Proto-Instance
        pinst = protodefs.Instance(name=inst.name)
        # Give it a Reference to its Module
        pinst.module.qn.domain = pmod.name.domain
        pinst.module.qn.name = pmod.name.name

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

        # FIXME: Parameters for Primitives/ External Modules
        # for pname, pval in inst.parameters_they_dont_have_yet:
        #     fail

        return pinst

    def export_concat(self, concat: signal.Concat) -> protodefs.Concat:
        """ Export (potentially recursive) Signal Concatenations """
        pconc = protodefs.Concat()
        for part in concat.parts:
            if isinstance(part, signal.Signal):
                psig = protodefs.Signal(name=part.name, width=part.width)
                pconn = protodefs.Connection()
                pconn.sig.CopyFrom(psig)
                pconc.parts.append(pconn)
            elif isinstance(part, signal.Slice):
                psig = protodefs.Slice(signal=part.signal.name, top=part.top, bot=part.bot)
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

