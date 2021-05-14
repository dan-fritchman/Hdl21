import copy
from typing import Callable, Union, Any, Optional
from pydantic.dataclasses import dataclass
from pydantic import ValidationError

# Local imports
from .module import Module
from .signal import Signal
from .generator import Generator, GeneratorCall


class Context:
    """ Elaboration Context """

    ...  # To be continued!


class Elaborator:
    """ Hierarchical Elaborator 
    Walks a hierarchy from `top`, calling Generators, fleshing out Modules, 
    and checking everything along the way. """

    def __init__(
        self, *, top: Union[Module, GeneratorCall], ctx: Context,
    ):
        self.top = top
        self.ctx = ctx

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
        gen = call.gen
        arg = call.arg

        # The main event: Run the generator-function
        if gen.usecontext:
            m = gen.func(arg, self.ctx)
        else:
            m = gen.func(arg)

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

        # Give the GeneratorCall a reference to its result
        call.result = m
        # If the Module that comes back is anonymous, give it a name equal to the Generator's
        if m.name is None:
            m.name = gen.func.__name__
        # And elaborate the module
        return self.elaborate_module(m)

    def elaborate_module(self, module: Module) -> Module:
        """ Elaborate Module `module`. First depth-first elaborates its Instances, 
        before creating any implicit Signals and connecting them. 
        Finally checks for connection-consistency with each Instance. """
        # FIXME: add traversal of any Interface connections
        from .instance import PortRef

        if not module.name:
            raise RuntimeError(
                f"Anonymous Module {module} cannot be elaborated (did you forget to name it?)"
            )
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
                    if sig is not None:  # Ruh roh! shorted between things
                        raise RuntimeError(
                            f"Invalid connection to {portconn}, shorting {[(p.inst.name, p.portname) for p in net]}"
                        )
                    sig = portconn
            # If we didn't find any, go about naming and creating one
            if sig is None:
                # The default name template is "_inst1_port1__inst2_port2_inst3_port3_"
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
                # Clone it and rename it
                sig = copy.copy(sig)
                sig.name = signame
            # Add it to the module namespace
            module.add(sig)
            # And re-connect it to each Instance
            for portref in net:
                portref.inst.conns[portref.portname] = sig

        # FIXME: Finally check instance connections line up!
        # And note that this thing's been through elaboration
        module._elaborated = True
        return module

    def elaborate_instance(self, inst: "Instance") -> Module:
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


def elaborate(top: Union[Module, Generator, GeneratorCall], params=None, ctx=None):
    """ In-Memory Elaborate Generator or Module `top`. """
    ctx = ctx or Context()
    if params is not None:
        if not isinstance(top, Generator):
            raise RuntimeError(
                f"Error attempting to elaborate non-generator {top} with non-null params {params}"
            )
        # Call the Generator here
        top = GeneratorCall(gen=top, arg=params)
    elab = Elaborator(top=top, ctx=ctx)
    return elab.elaborate()

