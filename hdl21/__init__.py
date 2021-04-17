""" 
Hdl21 Hardware Description Library 
"""

from .hdl21 import *
import builtins
import inspect
from enum import Enum
from textwrap import dedent
from dataclasses import dataclass, field
from typing import ClassVar, Optional


class ResolutionError(Exception):
    ...


class NoResult:
    # The cardinal value for unresolved references
    ...


primitive_types = (int, float, str, type(None))
banned_types = (dict, list, tuple)


def dotattrs(cls):
    """ Class decorator which adds the 'get DotAttrs' functionality """

    def __getattr__(self, name):
        if name in cls._protected:
            return cls.__getattribute__(name)
        d = DotAttr(name, self)
        d.deps.append(self)
        return d

    cls.__getattr__ = __getattr__
    return cls


def calls(cls):
    """ Class decorator which adds the 'call generates Calls' functionality """

    def __call__(self, *args, **kwargs):
        return Call(parent=self, args=args, kwargs=kwargs)

    cls.__call__ = __call__
    return cls


class ModuleDict:
    # A very helpful "dictionary"
    def __init__(self, name):
        self.name = name
        self.locals = locals()
        self.globals = globals()
        self.dunders = dict()
        self.defs = dict()
        self.names = dict()

    def __getitem__(self, key: str):
        if key == "__name__":  # This one is special, for some reason
            return self.name
        if key in self.dunders:
            return self.dunders[key]
        if key in self.defs:
            return self.defs[key]
        if key in self.names:
            return self.names[key]
        e = Name(name=key, parent=self)
        self.names.__setitem__(key, e)
        return e

    def __setitem__(self, key, val):
        if key.startswith("__"):
            return self.dunders.__setitem__(key, val)
        return self.defs.__setitem__(key, val)

    def __repr__(self):
        return f"ModuleDict({self.defs})"


@dotattrs
@calls
@dataclass
class Call:
    """ Function-style call into many of these objects """

    args: tuple
    kwargs: dict
    parent: ModuleDict = field(repr=False)
    _result: object = field(init=False, default=NoResult)
    _protected: ClassVar = field(default=["args", "kwargs", "parent", "deps"])

    @property
    def deps(self):
        return [self.parent] + list(self.args) + list(self.kwargs.values())


@dotattrs
@calls
@dataclass
class DotAttr:
    """ Dot-accessed attribute """

    name: str
    parent: object = field(repr=False)
    deps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, repr=False, default=NoResult)
    _protected: ClassVar = field(
        default=["name", "parent", "deps", "_result", "_resolve"]
    )


@dotattrs
@calls
@dataclass
class Name:
    """ Attribute in a Module class dict """

    name: str
    parent: ModuleDict = field(repr=False)
    deps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, repr=False, default=NoResult)
    _protected: ClassVar = field(default=["name", "parent", "deps"])

    _protected: ClassVar = field(
        default=["name", "parent", "deps", "_result", "_resolve"]
    )


class Resolver:
    def __init__(self, dct: ModuleDict, frames: list):
        self.dct = dct
        self.frames = frames

    def resolve_all(self) -> dict:
        return {k: self.resolve(v) for k, v in self.dct.defs.items()}

    def resolve(self, obj: object):
        """ Resolve unknown-type `obj` """
        if isinstance(obj, primitive_types):
            return obj
        if isinstance(obj, Name):
            return self.resolve_name(obj)
        if isinstance(obj, Call):
            return self.resolve_call(obj)
        if isinstance(obj, DotAttr):
            return self.resolve_dotattr(obj)
        raise TypeError

    def resolve_name(self, name: Name) -> object:
        if name._result is not NoResult:
            return name._result
        # if self.dct.defs[name.name] is not name:
        #     # Not sure how this would happen, something went wrong
        #     raise TabError
        for frame in self.frames:
            if name.name in frame.f_locals:
                name._result = frame.f_locals[name.name]
                return name._result
        raise ResolutionError

    def resolve_dotattr(self, dot: DotAttr):
        if dot._result is not NoResult:
            return dot._result
        parent = self.resolve(dot.parent)
        name = self.resolve(dot.name)
        dot._result = getattr(parent, name)
        return dot._result

    def resolve_call(self, call: Call):
        if call._result is not NoResult:
            return call._result
        args = (self.resolve(a) for a in call.args)
        kwargs = {k: self.resolve(v) for k, v in call.kwargs}
        func = self.resolve(call.parent)
        call._result = func(*args, **kwargs)
        return call._result


class ModuleMeta(type):
    _module_cls = None

    @classmethod
    def __prepare__(mcs, name, bases):
        # Cover the `Module` base-class
        if mcs._module_cls is None:
            if bases != ():
                raise RuntimeError
            return dict()
        # Cover custom sub-classes
        # Require they are sub-classes of our Module, and nothing else
        if bases != (Module,):
            raise RuntimeError
        return ModuleDict(name)

    def __new__(mcs, name, bases, dct):
        # Cover the `Module` base-class
        if mcs._module_cls is None:
            mcs._module_cls = type.__new__(mcs, name, bases, dct)
            return mcs._module_cls

        # And cover its custom sub-classes
        frames = []
        f = inspect.currentframe().f_back
        while f.f_locals is not f.f_globals:
            frames.append(f)
            f = f.f_back
        r = Resolver(dct, frames)
        d = r.resolve_all()
        return mcs.arrange(d, dct.name)

    @staticmethod
    def arrange(d: dict, name: str) -> "Module":
        """ Sort the contents of `d` into a module's type-based organization, 
        by ports, signals, instances, and so on. """
        m = Module(name)
        for k, v in d.items():
            if isinstance(v, Signal):
                v.name = k
                if v.visibility == SignalVisibility.PORT:
                    m.ports[k] = v
                else:
                    m.signals[k] = v
            elif isinstance(v, Instance):
                v.name = k
                m.signals[k] = v
            else:
                raise TypeError
        return m

    @staticmethod
    def order(dct: ModuleDict) -> list:
        """ Depth-first organize the definitions in `dct` """

        def _helper(obj, accum):
            # Check whether we've already visited this object,
            # And check whether it is a primitive, and so has no dependencies
            if obj in accum or isinstance(obj, primitive_types):
                return
            # Check for any explicitly disallowed types
            if isinstance(obj, banned_types):
                raise TypeError
            # Descend into each dependency, recursively accumulating theirs
            for dep in obj.deps:
                _helper(dep, accum)
            # And finally, add ourselves
            accum.append(obj)

        accum = []
        for obj in dct.defs.values():
            _helper(obj, accum)
        return accum


class Module(metaclass=ModuleMeta):
    def __init__(self, name):
        self.name = name
        self.ports = dict()
        self.signals = dict()
        self.instances = dict()

    def __call__(self, *_args, **_kwargs):
        """ Highly likely error: calling Modules in attempts to create Python-level instances, which they don't have.  """
        raise RuntimeError(
            dedent(
                f"""\
                Error: attempting to call (or instantiate) hdl21.Module {self.name}. 
                You probably want to pass its class-object to another function instead, 
                such as hdl21.Instance({self.name}), or retrieve its class-object attributes, 
                such as {self.name}.ports, {self.name}.instances, and so on."""
            )
        )

    def __init_subclass__(cls, /, **_kwargs):
        raise RuntimeError(
            dedent(
                f"""\
                Error attempting to create {cls.__name__}
                Sub-Typing hdl21.Module is not supported. """
            )
        )


class PortDir(Enum):
    INPUT = 0
    OUTPUT = 1
    INOUT = 2
    NONE = 3


class SignalVisibility(Enum):
    INTERNAL = 0
    PORT = 1


class Signal:
    def __init__(
        self,
        *,
        name=None,
        width=1,
        visibility=SignalVisibility.INTERNAL,
        direction=PortDir.NONE,
    ):
        self.name = name
        self.width = width
        self.visibility = visibility
        self.direction = direction


def Input(**kwargs):
    return Signal(visibility=SignalVisibility.PORT, direction=PortDir.INPUT)


def Output(**kwargs):
    return Signal(visibility=SignalVisibility.PORT, direction=PortDir.OUTPUT)


def Inout(**kwargs):
    return Signal(visibility=SignalVisibility.PORT, direction=PortDir.INOUT)


def Port(**kwargs):
    return Signal(visibility=SignalVisibility.PORT, direction=PortDir.NONE)


class Instance:
    def __init__(self, module: Module, conns: dict):
        self.module = module
        self.conns = conns
