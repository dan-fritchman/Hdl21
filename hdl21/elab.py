import copy
from enum import Enum, auto
from typing import Callable, Union, Any, Optional, Dict
from pydantic.dataclasses import dataclass
from pydantic import ValidationError

# Local imports
from .module import Module
from .instance import Instance
from .interface import Interface, InterfaceInstance
from .signal import Port, Signal, Visibility
from .generator import Generator, GeneratorCall


class Context:
    """ Elaboration Context """

    ...  # To be continued!


class GeneratorElaborator:
    """ Hierarchical Generator Elaborator 
    Walks a hierarchy from `top` calling Generators. """

    def __init__(
        self, top: Union[Module, GeneratorCall], ctx: Context,
    ):
        self.top = top
        self.ctx = ctx
        self.calls = dict()  # GeneratorCall ids to references
        self.modules = dict()  # Module ids to references

    def elaborate(self):
        """ Elaborate our top node """
        if isinstance(self.top, Module):
            return self.elaborate_module(self.top)
        if isinstance(self.top, GeneratorCall):
            return self.elaborate_generator_call(self.top)
        raise TypeError(
            f"Invalid Elaboration top-level {self.top}, must be a Module or Generator"
        )

    def elaborate_generator_call(self, call: GeneratorCall) -> Module:
        """ Elaborate Generator-function-call `call`. Returns the generated Module. """
        if call.result:  # Already done!
            return call.result

        # The main event: Run the generator-function
        if call.gen.usecontext:
            m = call.gen.func(call.arg, self.ctx)
        else:
            m = call.gen.func(call.arg)

        # Type-check the result
        # Generators may return other (potentially nested) generator-calls; unwind any of them
        while isinstance(m, GeneratorCall):
            # Note this should hit Python's recursive stack-check if it doesn't terminate
            m = self.elaborate_generator_call(m)
        # Ultimately they've gotta resolve to Modules, or they fail.
        if not isinstance(m, Module):
            raise TypeError(
                f"Generator {self.func.__name__} returned {type(m)}, must return Module."
            )

        # Give the GeneratorCall a reference to its result, and store it in our local dict
        call.result = m
        self.calls[id(call)] = call
        # If the Module that comes back is anonymous, give it a name equal to the Generator's
        # FIXME: cook up a unique name, mixing in the param-values
        if m.name is None:
            m.name = call.gen.func.__name__
        # And elaborate the module
        return self.elaborate_module(m)

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. First depth-first elaborates its Instances, 
        before creating any implicit Signals and connecting them. 
        Finally checks for connection-consistency with each Instance. """
        if id(module) in self.modules:  # Already done!
            return module

        if not module.name:
            raise RuntimeError(
                f"Anonymous Module {module} cannot be elaborated (did you forget to name it?)"
            )
        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        # Also visit interface instances, turning off their pre-elab magic
        for inst in module.interfaces.values():
            self.elaborate_interface_instance(inst)

        # Store a reference to the now-expanded Module in our cache, and return it
        self.modules[id(module)] = module
        return module

    def elaborate_interface_instance(self, inst: InterfaceInstance) -> None:
        """ Annotate each InterfaceInstance so that its pre-elaboration `PortRef` magic is disabled. """
        inst._elaborated = True

    def elaborate_instance(self, inst: Instance) -> Module:
        """ Elaborate a Module Instance. 
        Largely pushes through depth-first definition of the target-Module. 
        Connections, port-direction checking and the like are performed in `elaborate_module`. """
        inst._elaborated = True  # Turn off the instance's pre-elaboration magic
        if isinstance(inst.of, Generator):  # FIXME: maybe move this
            call = GeneratorCall(gen=inst.of, arg=inst.params)
            return self.elaborate_generator_call(call)
        if isinstance(inst.of, GeneratorCall):
            return self.elaborate_generator_call(call=inst.of)
        if isinstance(inst.of, Module):
            return self.elaborate_module(inst.of)
        raise TypeError(f"Invalid Instance of {inst.of}")


class ImplicitConnectionElaborator:
    """ Hierarchical Implicit-Connection Elaborator 
    Transform any implicit signals, i.e. port-to-port connections, into explicit ones. """

    def __init__(
        self, top: Module, ctx: Context,
    ):
        self.top = top
        self.ctx = ctx

    def elaborate(self):
        """ Elaborate our top node """
        if not isinstance(self.top, Module):
            raise TypeError
        return self.elaborate_module(self.top)

    def elaborate_instance(self, inst: Instance) -> Module:
        """ Elaborate a Module Instance. """
        if not inst.module:
            raise RuntimeError(f"Error elaborating non-Module Instance {inst}")
        return self.elaborate_module(inst.module)

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. First depth-first elaborates its Instances, 
        before creating any implicit Signals and connecting them. """

        from .instance import PortRef

        # Depth-first traverse instances, ensuring their targets are defined
        for inst in module.instances.values():
            self.elaborate_instance(inst)
        # Now work through expanding any implicit-ish connections, such as those from port to port.
        # Start by building an adjacency graph of every `PortRef` that's been instantiated
        portconns = dict()
        for inst in module.instances.values():
            for port, conn in inst.conns.items():
                if isinstance(conn, PortRef):
                    internal_ref = PortRef(inst, port)
                    portconns[internal_ref] = conn
        # Now walk through them, assigning each set to a net
        nets = list()
        while portconns:
            # Keep both a list for consistent ordering (we think), and a set for quick membership tests
            this_net_order = list()
            this_net_set = set()
            # Grab a random pair
            inner, outer = portconns.popitem()
            this_net_order.append(inner)
            this_net_set.add(inner)
            this_net_order.append(outer)
            this_net_set.add(outer)
            # If it's connected to others, grab those
            while outer in portconns:
                outer = portconns.pop(outer)
                if outer not in this_net_set:
                    this_net_set.add(outer)
                    this_net_order.append(outer)
            nets.append(this_net_order)
        # And for each net, find and/or create a Signal to replace all the PortRefs with.
        for net in nets:
            # Check whether any of them are connected to declared Signals.
            # And if any are, make sure there's only one
            sig = None
            for portref in net:
                portconn = portref.inst.conns.get(portref.portname, None)
                if isinstance(portconn, Signal):
                    if sig is not None and portconn is not sig:
                        # Ruh roh! shorted between things
                        raise RuntimeError(
                            f"Invalid connection to {portconn}, shorting {[(p.inst.name, p.portname) for p in net]}"
                        )
                    sig = portconn
            # If we didn't find any, go about naming and creating one
            if sig is None:
                # The default name template is "_inst1_port1__inst2_port2__inst3_port3_"
                # If this is (somehow) one of the user-defined Signal-names,
                # we continue appending a prepending underscores until it's not,
                # or until we hit a (hopefully safe) character limit.
                signame = "".join([f"_{p.inst.name}_{p.portname}_" for p in net])
                while signame in module.namespace:
                    if len(signame) > 511:  # Seems a reasonable limit? Maybe?
                        raise RuntimeError(
                            f"Could not name a Signal to connect to {[(p.inst.name, p.portname) for p in net]} (trying {signame})"
                        )
                    signame = "_" + signame + "_"

                # Create the Signal, looking up all its properties from the last Instance's Module
                # (If other instances are inconsistent, later stages will flag them)
                lastmod = portref.inst.module
                sig = lastmod.ports.get(portref.portname, None)
                if sig is None:  # Check its Interface-valued ports too!
                    sig = lastmod._interface_ports.get(portref.portname, None)
                if sig is None:
                    raise RuntimeError(
                        f"Invalid port {portref.portname} on Instance {portref.inst.name} in Module {module.name}"
                    )
                # Clone it, rename it, and add it to the Module namespace
                sig = copy.copy(sig)
                sig.name = signame
                module.add(sig)
            # And re-connect it to each Instance
            for portref in net:
                portref.inst.conns[portref.portname] = sig

        return module


@dataclass
class FlatInterface:
    """ Flattened Hierarchical Interface, resolved to constituent Signals """

    src: Interface  # Source/ Original Interface
    signals: Dict[str, Signal]  # Flattened Signals-Dict


class InterfaceFlattener:
    """ Interface-Flattening Elaborator Pass """

    def __init__(
        self, top: Module, ctx: Context,
    ):
        self.top = top
        self.ctx = ctx
        self.results = dict()  # Cache of Interfaces (ids) to FlatInterfaces

    def elaborate(self):
        """ Elaborate our top node """
        if isinstance(self.top, Module):
            return self.elaborate_module(self.top)
        if isinstance(self.top, GeneratorCall):
            return self.elaborate_generator_call(self.top)
        raise TypeError(
            f"Invalid Elaboration top-level {self.top}, must be a Module or Generator"
        )

    def elaborate_module(self, module: Module) -> Module:
        """ Depth-first flatten Module `module`s Interfaces, and reconnect them """
        raise NotImplementedError  # FIXME!
        # The depth-first part first
        for inst in module.instances.values():
            self.elaborate_instance(inst)

        # FIXME: connections are work in progress
        from .signal import Visibility, PortDir

        while module.interfaces:
            _name, intf = module.interfaces.popitem()
            flat = self.elaborate_interface_instance(intf)
            for sig in flat.signals.values():
                sig = copy.copy(sig)
                signame = f"_{intf.name}_{sig.name}_"
                while signame in module.namespace:
                    if len(signame) > 511:  # Seems a reasonable limit? Maybe?
                        raise RuntimeError(
                            f"Could not name a flattened Signal for {sig.name} in Module {module.name} (trying {signame})"
                        )
                    signame = "_" + signame + "_"

                if intf.port:
                    vis_ = Visibility.PORT
                    if intf.role is None:
                        dir_ = PortDir.NONE
                    elif intf.role == sig.src:
                        dir_ = PortDir.OUTPUT
                    elif intf.role == sig.dest:
                        dir_ = PortDir.INPUT
                    else:
                        dir_ = PortDir.NONE
                else:
                    vis_ = Visibility.INTERNAL
                    dir_ = PortDir.NONE
                # Apply all these attributes to our new Signal
                sig.name = signame
                sig.visibility = vis_
                sig.direction = dir_
                # And add it to the Module namespace
                module.add(sig)

        return module

    def elaborate_interface_instance(self, inst: InterfaceInstance) -> FlatInterface:
        """ Elaborate an Interface Instance. 
        Really meaning get a flattened definition of its target Interface. 
        All connection-checking is done elsewhere. """
        return self.flatten_interface(inst.of)

    def flatten_interface(self, intf: Interface) -> FlatInterface:
        """ Convert nested Interface-definition `intf` into a flattened `FlatInterface` of scalar Signals """
        if id(intf) in self.results:  # Already done
            return self.results[id(intf)]

        # Create the flattened version, initializing it with `intf`s scalar Signals
        flat = FlatInterface(src=intf, signals=copy.copy(intf.signals))
        # Depth-first walk any interface-instance's definitions, flattening them
        for i in intf.interfaces.values():
            iflat = self.elaborate_interface_instance(i)
            # Create Signals for each
            # Note child Interfaces may be re-used elsewhere, so their returning Signals are (deep) copied.
            signals = copy.deepcopy(list(iflat.signals.values()))
            # The naming convention for flattened signals is "_instname_signame_"
            # If this is (somehow) a name the designer actually chose,
            # Append and prepend underscores until it's not, or until we hit a length-limit.
            for sig in signals:
                signame = f"_{i.name}_{sig.name}_"
                while signame in flat.signals:
                    if len(signame) > 511:  # Seems a reasonable limit? Maybe?
                        raise RuntimeError(
                            f"Could not name a flattened Signal for {sig.name} in Interface {intf.name} (trying {signame})"
                        )
                    signame = "_" + signame + "_"
                # Rename the signal, and store it in our flat-intf
                sig.name = signame
                flat.signals[signame] = sig

        # Store and return the flattened version
        self.results[id(intf)] = flat
        return flat

    def elaborate_instance(self, inst: Instance) -> Module:
        """ Elaborate a Module Instance. """
        if not inst.module:
            raise RuntimeError(f"Error elaborating non-Module Instance {inst}")
        return self.elaborate_module(inst.module)


class ElabPasses(Enum):
    """ Enumerated Elaborator Passes """

    EXPAND_GENERATORS = auto()
    EXPAND_IMPLICIT_CONNS = auto()
    FLATTEN_INTERFACES = auto()


# Pass-functions have the signature
# callable(top: Union[Module, GeneratorCall], ctx: Context) -> Module
# (Most in fact require `Module` instead of `GeneratorCall`)
default_passes = [ElabPasses.EXPAND_GENERATORS, ElabPasses.EXPAND_IMPLICIT_CONNS]


def expand_generators(top: Union[Module, GeneratorCall], ctx: Context) -> Module:
    elab = GeneratorElaborator(top=top, ctx=ctx)
    return elab.elaborate()


def expand_implicit_connections(top: Module, ctx: Context) -> Module:
    if not isinstance(top, Module):
        raise TypeError
    elab = ImplicitConnectionElaborator(top=top, ctx=ctx)
    return elab.elaborate()


def flatten_interfaces(top: Module, ctx: Context) -> Module:
    if not isinstance(top, Module):
        raise TypeError
    elab = InterfaceFlattener(top=top, ctx=ctx)
    return elab.elaborate()


pass_funcs = {
    ElabPasses.EXPAND_GENERATORS: expand_generators,
    ElabPasses.EXPAND_IMPLICIT_CONNS: expand_implicit_connections,
    ElabPasses.FLATTEN_INTERFACES: flatten_interfaces,
}

# Type short-hand for elaborate-able types
Elabable = Union[Module, Generator, GeneratorCall]


def elaborate(top: Elabable, params=None, ctx=None, passes=None):
    """ In-Memory Elaboration of Generator or Module `top`. """
    ctx = ctx or Context()
    passes = passes or copy.copy(default_passes)
    if params is not None:
        if not isinstance(top, Generator):
            raise RuntimeError(
                f"Error attempting to elaborate non-generator {top} with non-null params {params}"
            )
        # Call the Generator here
        top = GeneratorCall(gen=top, arg=params)

    # Pass `top` through each of our passes in order
    res = top
    for pass_ in passes:
        res = pass_funcs[pass_](top=res, ctx=ctx)
    return res

