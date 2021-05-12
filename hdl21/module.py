"""
# hdl21.module 

The `Module` Module (get it?)
This module primarily defines the core circuit-reuse element `hdl21.Module`. 
It also includes the fun machinery for class-syntax creation of `Module`s, 
enabled by a custom metaclass and its partner custom dictionary, 
which unwind `Module` sub-class-body contents in dataflow order. 
"""

import builtins
import inspect

from textwrap import dedent
from dataclasses import dataclass, field
from typing import ClassVar, Optional, Union, Callable, Any


class ModuleMeta(type):
    """ 
    Metaclass enabling class-style definition of `Module`s. 
    Works in conjunction with `ModuleDict`, the custom dictionary type used during class-bodies, 
    to enable dependency-order definition of `Module` attributes. 

    During custom `Module` definition via class-style syntax such as:

    ```
    class MyModule(Module):
        a = Signal()
        b = Input()
        c = Output()
        d = Instance(OtherModule)(a=a, b=b, c=c)
    ```

    How this happens: 

    * Before class-body execution, `ModuleMeta.__prepare__` creates a `ModuleDict` to use for the class-body 
    * During class-body execution, the `ModuleDict` creates a graph of dataflow-ordered `Node` objects (`Name`, `Call`, `DotAttr`, et al)
    * After class-body execution, `ModuleMeta.__new__` resolves all of these nodes 
    * Doing so frequently requires walking up the recursive symbol-table at the time of class-definition. 
      These layers are retrieved via the `inspect` module, and produced as a bottom-to-top list by `ModuleMeta.stack`
    * The resolved values are added and organized into a newly-created `Module` instance. 

    `ModuleMeta` is also a singleton. Only only instance of it, the `Module` class, can ever be created. 
    Further apparent "subclasses" of `Module` actually produce *instances* of `Module` instead. 
    The `Module` class-object is also stored as `ModuleMeta._the_module_cls`. 
    Both its `__prepare__` and `__new__` methods are heavily special-cased for their initial run, 
    which creates the `Module` class-object. 
    """

    _the_module_cls = None

    @classmethod
    def __prepare__(mcs, name, bases):
        # Cover the `Module` base-class
        if mcs._the_module_cls is None:
            if bases != () or name != "Module":
                raise RuntimeError(
                    "hdl21 Internal Error: {name} defined where hdl21.Module class-definition expected/"
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
        if mcs._the_module_cls is None:
            mcs._the_module_cls = type.__new__(mcs, name, bases, dct)
            return mcs._the_module_cls

        # And cover every other case, its custom sub-classes
        r = Resolver(dct, mcs.stack())
        d = r.resolve_all()
        return mcs.arrange(d, dct.name)

    @staticmethod
    def stack() -> list:
        """ Retrieve the recursive symbol-table from `inspect` frames, up to globals. """
        return [fi.frame for fi in inspect.stack()[2:]]

    @staticmethod
    def arrange(d: dict, name: str) -> "Module":
        """ Sort the contents of `d` into a module's type-based organization, 
        by ports, signals, instances, and so on. """
        m = Module(name=name)
        for k, v in d.items():
            setattr(m, k, v)
        return m


class Module(metaclass=ModuleMeta):
    """ 
    # Module
    The central element of hardware re-use. 
    """

    def __init__(self, *, name=None):
        self.name = name
        self.ports = dict()
        self.signals = dict()
        self.instances = dict()
        self.instarrays = dict()
        self.interfaces = dict()
        self.namespace = dict()  # Combination of all these
        self._genparams = None
        self._initialized = True

    def __setattr__(self, key: str, val: object):
        """ Set-attribute over-ride, organizing into type-based containers """
        from .signal import Signal, Visibility
        from .instance import Instance, InstArray
        from .interface import InterfaceInstance

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
            if val.visibility == Visibility.PORT:
                self.ports[key] = val
            else:
                self.signals[key] = val
        elif isinstance(val, Instance):
            val.name = key
            self.instances[key] = val
            self.namespace[key] = val
        elif isinstance(val, InstArray):
            val.name = key
            self.instarrays[key] = val
            self.namespace[key] = val
        elif isinstance(val, InterfaceInstance):
            val.name = key
            self.interfaces[key] = val
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

    def __init_subclass__(cls, *_args, **_kwargs):
        """ Sub-Classing Disable-ization """
        raise RuntimeError(
            dedent(
                f"""\
                Error attempting to create {cls.__name__}
                Sub-Typing hdl21.Module is not supported. """
            )
        )


class ModuleDict:
    """ 
    # Module Class-Body Dictionary 
    Much of the `ModuleMeta` magic is accomplished here, via the behaviors of `ModuleDict`. 

    * When retrieving a key, ModuleDicts *never* report failure via `KeyError`
    * Attempts to retrieve missing keys generate and return new `Name`s, 
      references which must be defined by class-definition completion 
    * This causes all accesses to produce one of the graph `Node` types: Names, DotAttrs, and Calls
    * These graphs nodes track sets of forward and reverse dependences `fdeps` and `rdeps`
    * Upon insertion of a new item via __setitem__, ModuleDict updates any dependences 
      if the new key was previously generated as a `Name`

    Attributes are stored in internal sub-dictionaries. 
    The `defs` dict is most similar to the typical class-dict, holding class-attribute definitions. 
    Double-underscore attributes (`dunders`) are treated and stored separately. 
    """

    def __init__(self, name):
        self.name = name
        self.dunders = dict()
        self.defs = dict()
        self.names = dict()

    def __getitem__(self, key: str):
        if key == "__name__":
            # This one is special, for some reason Python gets it from the dict.
            # Most other dunders are just set on the class-object.
            return self.name
        # Check our internal dicts
        if key in self.dunders:
            return self.dunders[key]
        if key in self.defs:
            return self.defs[key]
        if key in self.names:
            return self.names[key]
        # `key` is not defined - create, store, and return a new `Name`
        e = Name(_name=key, _parent=self)
        self.names[key] = e
        return e

    def __setitem__(self, key, val):
        if key.startswith("__"):
            return self.dunders.__setitem__(key, val)
        if key in self.names:
            # Replacing a `Name` with a new value.
            # Requires removing the `Name`, and updating anything that depends on it.
            old = self.names.pop(key)
            for rdep in old._rdeps:
                rdep._replace(old=old, new=val)
        if not getattr(val, "__nodeclass__", False):
            val = Val(val)
        # And store this in our definitions
        self.defs[key] = val

    def __repr__(self):
        return f"ModuleDict({self.defs})"


class NoResult:
    # The cardinal value for unresolved references
    ...


# Protected attributes for the get & set attr overrides
_protected = [
    "_name",
    "_parent",
    "_args",
    "_kwargs",
    "_func",
    "_val",
    "_fdeps",
    "_rdeps",
    "_result",
    "_replace",
]


def dotattrs(cls):
    """ Class decorator which adds the 'get `DotAttr`s' functionality """

    def __getattr__(self, key):
        if key in _protected:
            return self.__getattribute__(key)
        # Create the DotAttr with ourselves as parent, and add it as a (reverse) dependency
        d = DotAttr(_name=key, _parent=self)
        self._rdeps.append(d)
        return d

    cls.__getattr__ = __getattr__
    return cls


def calls(cls):
    """ Class decorator which adds the 'call generates Calls' functionality """

    def __call__(self, *args, **kwargs):
        # Create the call, and add it to our reverse-dependences
        c = Call(_func=self, _args=args, _kwargs=kwargs)
        self._rdeps.append(c)
        # If any arguments are Nodes, they need the Call as a reverse-dependence too
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
        # Allow setting the protected attributes, so this party gets started
        # A potential enhancement would be setting an initialization flag
        # To only allow these once
        if key in _protected:
            return super(cls, self).__setattr__(key, val)
        # No other set-attr-ing allowed.
        raise RuntimeError(
            f"Invalid attempt to set dot-access attribute {key} inside Module-definition block"
        )

    cls.__setattr__ = __setattr__
    return cls


def nodeclass(cls: type) -> type:
    """ Apply all our decorators, creating a dependency-graph node. """
    cls = dataclass(cls)
    cls = no_setattr(cls)
    cls = dotattrs(cls)
    cls = calls(cls)
    cls.__nodeclass__ = True
    return cls


@nodeclass
class Call:
    """ Function-style call into many of these objects """

    _func: Callable
    _args: tuple
    _kwargs: dict
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


@nodeclass
class DotAttr:
    """ Dot-accessed attribute """

    _name: str
    _parent: object = field(repr=False)
    _rdeps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, repr=False, default=NoResult)

    @property
    def _fdeps(self):
        """ A dot-access's sole (forward) dependence is its Parent. """
        return [self._parent]

    def _replace(self, old, new):
        """ Replace (forward) dependency `old` with `new` """
        for idx, val in enumerate(self._fdeps):
            if val is old:
                self._fdeps[idx] = new


@nodeclass
class Name:
    """ Unresolved Name Reference """

    _name: str
    _parent: ModuleDict = field(repr=False)
    _rdeps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, repr=False, default=NoResult)


@nodeclass
class Val:
    """ Value, usually a literal assigned to a class-key """

    _val: Any
    _rdeps: list = field(init=False, default_factory=list)
    _result: object = field(init=False, repr=False, default=NoResult)


# Graph-Nodes are the Union of these three
Node = Union[Name, DotAttr, Call, Val]


class ResolutionError(Exception):
    ...


# Primitive & built-in types which are allowed, and resolve to themselves.
_primitive_types = (int, float, str, type(None))


class Resolver:
    """ Dependency-Graph Resolver 
    Walks all items in input-ModuleDict `dct`, 
    recursively resolving its definitions and their dependencies. """

    def __init__(self, dct: ModuleDict, frames: list):
        self.dct = dct
        self.frames = frames
        self.connection_calls = list()

    def resolve_all(self) -> dict:
        """ Primary API method. Resolve everything in `self.dct`. """
        # Resolve all of the class attributes
        results = {k: self.resolve(v) for k, v in self.dct.defs.items()}

        # Finally, make our connection-calls.
        for call in self.connection_calls:
            func = self.resolve(call._func)
            args = (self.resolve(a) for a in call._args)
            kwargs = {k: self.resolve(v) for k, v in call._kwargs.items()}
            f2 = func(*args, **kwargs)
            # Instance connection-calls return themselves, a property we can check for!
            if f2 is not func:
                raise ResolutionError(
                    f"Internal Error: hdl21 connecting non-Instance {func}"
                )
        return results

    def resolve(self, obj: object) -> None:
        """ Resolve unknown-type `obj` """
        if isinstance(obj, _primitive_types):
            return obj
        if isinstance(obj, Name):
            return self.resolve_name(obj)
        if isinstance(obj, Call):
            return self.resolve_call(obj)
        if isinstance(obj, DotAttr):
            return self.resolve_dotattr(obj)
        if isinstance(obj, Val):
            return self.resolve_val(obj)
        raise TypeError(f"Invalid attribute {obj} in Module {self.dct.name}")

    def resolve_val(self, val: Val) -> object:
        """ Resolve a (likely literal) value """
        if val._result is not NoResult:  # Already computed
            return val._result
        val._result = self.resolve(val._val)
        return val._result

    def resolve_name(self, name: Name) -> object:
        """ Resolve a named identifier """
        if name._result is not NoResult:  # Already computed
            return name._result
        if name._name in self.dct.defs:  # Defined in our class-def
            return self.resolve(self.dct.defs[name._name])
        # Hasn't been found - start walking the symbol-table
        for frame in self.frames:
            if name._name in frame.f_locals:
                name._result = frame.f_locals[name._name]
                return name._result
            # Note `f_globals` is *not* the top-level namespace, which would be identical for every frame.
            # Nor does it equal the parent frame's `f_locals`.
            # The difference seems particularly pertinent with `import as` statements.
            if name._name in frame.f_globals:
                name._result = frame.f_globals[name._name]
                return name._result
        # Not found anywhere in the symbol-table, check built-in definitions e.g. `zip`, `range` as well.
        if name._name in builtins.__dict__:
            name._result = getattr(builtins, name._name)
            return name._result
        raise ResolutionError(f"Error resolving {name._name} in {self.dct.name}")

    def resolve_dotattr(self, dot: DotAttr) -> object:
        """ Resolve a dot-access attribute `dot`. 
        Recursively calls `resolve` for dot's parent, to ensure it's been resolved first. """
        if dot._result is not NoResult:  # Already computed
            return dot._result
        # Resolve the parent, then getattr-it, store and return the result
        parent = self.resolve(dot._parent)
        dot._result = getattr(parent, dot._name)
        return dot._result

    def resolve_call(self, call: Call) -> object:
        """ Resolve a function call. 
        Recursively resolves its function object and arguments,
        before calling the resolved function and returning the result. """
        from .instance import Instance, InstArray

        if call._result is not NoResult:  # Already computed, generally via a `Name`
            return call._result
        # Resolve our function-object
        func = self.resolve(call._func)
        # Special case for connections, which often create graph-cycles.
        # Set these aside for later in our `connection_calls` list.
        if isinstance(func, (Instance, InstArray)):
            self.connection_calls.append(call)
            call._result = func
            return func
        # Resolve our arguments
        args = (self.resolve(a) for a in call._args)
        kwargs = {k: self.resolve(v) for k, v in call._kwargs.items()}
        # Call it, store the result, and return it
        call._result = func(*args, **kwargs)
        return call._result

