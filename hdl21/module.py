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
_protected = [
    "_name",
    "_parent",
    "_args",
    "_kwargs",
    "_func",
    "_fdeps",
    "_rdeps",
    "_result",
    "_resolve",
    "_replace",
]


def dotattrs(cls):
    """ Class decorator which adds the 'get DotAttrs' functionality """

    def __getattr__(self, key):
        if key in _protected:
            return self.__getattribute__(key)
        d = DotAttr(key, self)
        d._fdeps.append(self)
        self._rdeps.append(d)
        return d

    cls.__getattr__ = __getattr__
    return cls


def calls(cls):
    """ Class decorator which adds the 'call generates Calls' functionality """

    def __call__(self, *args, **kwargs):
        c = Call(_func=self, _args=args, _kwargs=kwargs)
        self._rdeps.append(c)
        for a in args:
            if hasattr(a, "_rdeps"):
                a._rdeps.append(c)
        for v in kwargs.values():
            if hasattr(v, "_rdeps"):
                v._rdeps.append(c)
        return c

    cls.__call__ = __call__
    return cls


def no_setattr(cls):
    """ Class decorator removes setattr functionality """

    def __setattr__(self, key, val):
        if key not in _protected:
            raise TabError
        super(cls, self).__setattr__(key, val)

    cls.__setattr__ = __setattr__
    return cls


class ModuleDict:
    # A very helpful "dictionary"
    def __init__(self, name):
        self.name = name
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
        e = Name(_name=key, _parent=self)
        self.names.__setitem__(key, e)
        return e

    def __setitem__(self, key, val):
        if key.startswith("__"):
            return self.dunders.__setitem__(key, val)
        if key in self.names:
            old = self.names[key]
            if old._fdeps:
                raise TabError
            # Replace the old Name in each reverse dependency
            for rdep in old._rdeps:
                rdep._replace(old=old, new=val)
        return self.defs.__setitem__(key, val)

    def __repr__(self):
        return f"ModuleDict({self.defs})"


@calls
@dotattrs
@no_setattr
@dataclass
class Call:
    """ Function-style call into many of these objects """

    _args: tuple
    _kwargs: dict
    _func: object = field(repr=False)
    _rdeps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, default=NoResult)

    @property
    def _fdeps(self):
        """ Forward dependencies: the target function, and all its arguments """
        return [self._func] + list(self._args) + list(self._kwargs.values())

    def _replace(self, old, new):
        """ Replace (forward) dependency `old` with `new` """
        if old is self._func:
            self._func = new
        for idx, val in enumerate(self._args):
            if val is old:
                self._args[idx] = new
        for k, v in self._kwargs.items():
            if v is old:
                self._kwargs[k] = new


@calls
@dotattrs
@no_setattr
@dataclass
class DotAttr:
    """ Dot-accessed attribute """

    _name: str
    _parent: object = field(repr=False)
    _fdeps: list = field(init=False, default_factory=list)
    _rdeps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, repr=False, default=NoResult)

    def _replace(self, old, new):
        """ Replace (forward) dependency `old` with `new` """
        for idx, val in enumerate(self._fdeps):
            if val is old:
                self._fdeps[idx] = new


@calls
@dotattrs
@no_setattr
@dataclass
class Name:
    """ Unresolved Name Reference """

    _name: str
    _parent: ModuleDict = field(repr=False)
    _fdeps: list = field(init=False, default_factory=list)
    _rdeps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, repr=False, default=NoResult)


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
        for frame in self.frames:
            if name._name in frame.f_locals:
                name._result = frame.f_locals[name._name]
                return name._result
        if name._name in builtins.__dict__:
            name._result = getattr(builtins, name._name)
            return name._result
        raise ResolutionError(f"Error resolving {name._name} in {self.dct.name}")

    def resolve_dotattr(self, dot: DotAttr):
        if dot._result is not NoResult:
            return dot._result
        parent = self.resolve(dot._parent)
        name = self.resolve(dot._name)
        dot._result = getattr(parent, name)
        return dot._result

    def resolve_call(self, call: Call):
        if call._result is not NoResult:
            return call._result
        args = (self.resolve(a) for a in call._args)
        kwargs = {k: self.resolve(v) for k, v in call._kwargs.items()}
        func = self.resolve(call._func)
        call._result = func(*args, **kwargs)
        return call._result


class ModuleMeta(type):
    _module_cls = None

    @classmethod
    def __prepare__(mcs, name, bases):
        # Cover the `Module` base-class
        if mcs._module_cls is None:
            if bases != ():
                raise RuntimeError(
                    "Hdl21 Internal Error: {name} defined where hdl21.Module definition expected/"
                )
            return dict()
        # Cover custom sub-classes
        # Require they are sub-classes of our Module, and nothing else
        if bases != (Module,):
            raise RuntimeError(
                f"Class {name} defined with base-classes {bases}. hdl21.Modules do not support multiple inheritance. "
            )
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
        m = Module(name=name)
        for k, v in d.items():
            setattr(m, k, v)
        return m


class Module(metaclass=ModuleMeta):
    def __init__(self, *, name=None):
        self.name = name
        self.ports = dict()
        self.signals = dict()
        self.instances = dict()
        self.namespace = dict()  # Combination of all these
        self._genparams = None
        self._initialized = True

    def __setattr__(self, key: str, val: object):
        """ Set-attribute over-ride, organizing into type-based containers """
        if not getattr(self, "_initialized", False) or key.startswith("_"):
            return super().__setattr__(key, val)

        # Protected attrs - the internal dicts
        banned = ["ports", "signals", "instances", "namespace"]
        if key in banned:
            raise RuntimeError(
                f"Error attempting to over-write protected attribute {key} of Module {self}"
            )
        # Special case(s)
        if key == "name":
            return super().__setattr__(key, val)

        # Type-based organization
        if isinstance(val, Signal):
            val.name = key
            self.namespace[key] = val
            if val.visibility == SignalVisibility.PORT:
                self.ports[key] = val
            else:
                self.signals[key] = val
        elif isinstance(val, Instance):
            val.name = key
            self.instances[key] = val
            self.namespace[key] = val
        else:
            raise TypeError(f"Invalid Module attribute {val} for {self}")

    def __getattr__(self, key):
        ns = self.__getattribute__("namespace")
        if key in ns:
            return ns[key]
        return object.__getattribute__(self, key)

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
        """ Sub-Classing Disable-ization """
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
    def __init__(self, module: Module, **conns: dict):
        self.module = module
        self.conns = conns
