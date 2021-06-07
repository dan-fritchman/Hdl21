"""
hdl21 ProtoBuf Import 
"""
import copy
from types import SimpleNamespace

# Local imports
# Proto-definitions
from . import circuit_pb2 as protodefs

# HDL
from ..module import Module
from ..instance import Instance
from ..signal import Signal, Port, PortDir


def from_proto(pkg: protodefs.Package) -> SimpleNamespace:
    """ Convert Proto-defined Package `pkg` to a namespace-full of Modules. """
    importer = ProtoImporter(pkg)
    return importer.import_()


class ProtoImporter:
    """ Protobuf Package Importer. 
    Collects all `Modules` defined in Protobuf-sourced primary-argument `pkg` into a Python `types.SimpleNamespace`. """

    def __init__(self, pkg: protodefs.Package):
        self.pkg = pkg
        self.modules = dict()  # Dict of qual-names to Modules
        self.ns = SimpleNamespace()
        self.ns.name = pkg.name
        if pkg.name != "THIS_LIBRARY":
            raise ValueError(
                f"Invalid package name {pkg.name}, scoping coming soon"
            )  # FIXME!

    def import_(self) -> SimpleNamespace:
        """ Import the top-level `Package` to a Python namespace """
        # Walk through each proto-defined Module
        for pmod in self.pkg.modules:
            self.import_module(pmod)
        # Return our collected namespace
        return self.ns

    def import_module(self, pmod: protodefs.Module) -> Module:
        """ Convert Proto-Module `pmod` to an `hdl21.Module` """
        if (pmod.name.domain, pmod.name.name) in self.modules:  # Already done!
            return self.modules[(pmod.name.domain, pmod.name.name)]

        # Create the Module
        module = Module()
        # FIXME: whatever to do with these qualified path-names
        module.name = pmod.name.name

        # Import its ports
        for pport in pmod.ports:
            dir_ = self.import_port_dir(pport)
            port = Port(
                name=pport.signal.name, width=pport.signal.width, direction=dir_,
            )
            module.add(port)

        # Import its signals
        for psig in pmod.signals:
            sig = Signal(name=psig.name, width=psig.width)
            module.add(sig)

        # Lap through instances, connecting them, creating internal Signals if necessary (bleh)
        for pinst in pmod.instances:
            inst = self.import_instance(pinst)
            module.add(inst)

            # Make its connections
            for pname, sname in pinst.connections.items():
                if pname not in inst.module.ports:
                    raise RuntimeError(
                        f"Invalid Port {pname} on Instance {inst.name} of Module {inst.module.name} in Module {module.name}"
                    )
                # Grab this Signal, if it exists
                sig = module.namespace.get(sname, None)
                if sig is None:
                    # This block has held, at some points in code-history,
                    # the SPICE-style "create nets from thin air" behavior.
                    # That's outta here; undeclared signals produce errors instead.
                    raise RuntimeError(
                        f"Invalid Signal {sname} on Instance {inst.name} in Module {module.name}"
                    )

                # And connect it to the Instance
                setattr(inst, pname, sig)

        # Add the Module to our cache and return-namespace, and return it
        self.modules[(pmod.name.domain, pmod.name.name)] = module
        setattr(self.ns, module.name, module)
        return module

    def import_instance(self, pinst: protodefs.Instance) -> Instance:
        """ Convert Proto-Instance `pinst` to an `hdl21.Instance`. 
        Requires an available Module-definition to be referenced. 
        Connections are *not* performed inside this method. """

        module = self.import_module_reference(pinst.module)
        return Instance(name=pinst.name, of=module)

    def import_module_reference(self, ref: protodefs.Reference) -> Module:
        """ Resolve a Proto-defined `Reference` to an in-memory `Module`. 
        Requires that `pinst.module` be defined by the time this is called. 
        Typically this requires dependency-ordering of the Module definitions.
        """

        # Also a small piece of proof that Google hates Python.
        if ref.WhichOneof("to") != "qn":  # Only `QualifiedName` as valid and supported
            raise ValueError(f"Invalid reference {ref}")
        if ref.qn.domain != "THIS_LIBRARYS_FLAT_NAMESPACE":
            raise ValueError(f"Invalid reference {ref}; qualified names coming soon")

        key = (ref.qn.domain, ref.qn.name)
        module = self.modules.get(key, None)
        if module is None:
            raise RuntimeError(f"Invalid undefined Module {key} ")
        return module

    def import_port_dir(self, pport: protodefs.Port) -> PortDir:
        # Convert between Port-Direction Enumerations
        if pport.direction == protodefs.Port.Direction.INPUT:
            return PortDir.INPUT
        if pport.direction == protodefs.Port.Direction.OUTPUT:
            return PortDir.OUTPUT
        if pport.direction == protodefs.Port.Direction.INOUT:
            return PortDir.INOUT
        if pport.direction == protodefs.Port.Direction.NONE:
            return PortDir.NONE
        raise ValueError

