"""
Hdl21 Parameters and Param-Classes 
"""

from typing import Optional, Any
import dataclasses
import json
import pickle
import hashlib
import pydantic


# Import a few likely common Exception-types,
# Not used directly here, but likely by users and tests
from pydantic import ValidationError
from dataclasses import FrozenInstanceError


class _Default:
    """ The cardinal value for unspecified parameter-declaration defaults.
    Normally the class-object itself would work for this, but `pydantic.dataclasses`
    seems to have some problems accepting class-objects. 
    https://github.com/samuelcolvin/pydantic/issues/1537
    So we create this singleton instance `_default`, AKA `_Default._the_one`. """

    _the_one = None

    def __new__(cls, *_, **__):
        if cls._the_one is None:
            cls._the_one = super().__new__(cls)
        return cls._the_one


# Create that singleton
_default = _Default()


def paramclass(cls: type) -> type:
    """ Parameter-Class Creation Decorator 

    Transforms a class-definition full of Params into a type-validated dataclass, 
    with methods for default value and description-dictionary retrieval. 

    Hdl21's `paramclass`es are immutable, strongly-typed data-storage structures. 
    They are defined through a syntax similar to `@dataclass`, but using the `Param` 
    constructor, and assignment rather than type annotation. 

    @paramclass
    class C:
        reqd = Param(dtype=int, desc="A Required Parameter")
        optn = Param(dtype=int, desc="An Optional Parameter", default=11)

    `Param`s each have required datatype (`dtype`) and description (`desc`) fields, 
    and optional default values. 
    Each `paramclass` constructor can be called with ordered arguments, 
    in the order defined in the `paramclass`, or with named arguments. 
    Named arguments are highly recommended for more than a single parameter. 
    Note Python's function-argument ordering requirements also dictate 
    that all `paramclass` required-arguments be declared *before* any optional arguments. 
    This also reinforces good practice for communicating which parameters are required.

    Each `paramclass` comes with class-methods `descriptions` and `defaults`, 
    which return dictionaries of the parameter names to descriptions and 
    names to default values (for those with defaults), respectively. 
    
    Requirements of the input `cls`:
    * *All* non-Python-internal fields must be of type `Param`
    * Inheritance is not supported
    """
    if cls.__bases__ != (object,):
        raise RuntimeError(f"Invalid @hdl21.paramclass inheriting from {cls.__bases__}")
    protected_names = ["descriptions", "defaults"]
    dunders = dict()
    params = dict()
    # Take a lap through the class dictionary, type-check everything and grab Params
    for key, val in cls.__dict__.items():
        if key in protected_names:
            raise RuntimeError(f"Invalid field name {key} in paramclass {cls}")
        elif key.startswith("__"):
            dunders[key] = val
        elif isinstance(val, Param):
            params[key] = val
        else:
            raise RuntimeError(
                f"Invalid class-attribute {key} in paramclass {cls}. All attributes should be `hdl21.Param`s."
            )
    # Translate the Params into dataclass.field-compatible tuples
    fields = list()
    for name, par in params.items():
        field = [name, par.dtype]
        if par.default is not _default:
            field.append(dataclasses.field(default=par.default))
        # Default factories: not supported, yet. See `Param` below.
        # elif par.default_factory is not _default:
        #     field.append(dataclasses.field(default_factory=par.default_factory))
        fields.append(tuple(field))
    # Add a few helpers to the class namespace
    ns = dict(
        __params__=params,
        __paramclass__=True,
        descriptions=classmethod(
            lambda cls: {k: v.desc for k, v in cls.__params__.items()}
        ),
        defaults=classmethod(
            lambda cls: {
                k: v.default
                for k, v in cls.__params__.items()
                if v.default is not _default
            }
        ),
    )
    # Create ourselves a (std-lib) dataclass
    cls = dataclasses.make_dataclass(cls.__name__, fields, namespace=ns, frozen=True)
    # Pass this through the pydantic dataclass-decorator-function
    cls = pydantic.dataclasses.dataclass(cls, frozen=True)
    # Pydantic seems to want to add this one *after* class-creation
    def _brick_subclassing_(cls, *_, **__):
        raise RuntimeError(
            f"Error: attempt to sub-class `hdl21.paramclass` {cls} is not supported"
        )

    cls.__init_subclass__ = classmethod(_brick_subclassing_)
    # And don't forget to return it!
    return cls


def isparamclass(cls: type) -> bool:
    """ Boolean indication of whether `cls` has been `@paramclass`-decorated """
    return getattr(cls, "__paramclass__", False)


@pydantic.dataclasses.dataclass
class Param:
    """ Parameter Declaration """

    dtype: Any  # Datatype. Required
    desc: str  # Description. Required
    default: Optional[Any] = _default  # Default Value. Optional

    # Default factories are supported in std-lib dataclasses, but "in beta" in `pydantic.dataclasses`.
    # default_factory: Optional[Any] = _default  # Default Call-Factory


def _unique_name(params: Any) -> str:
    """ Create a unique name for parameter-class instance `params` """
    if not isparamclass(params):
        raise RuntimeError(f"Invalid parameter-class instance {params}")

    # Determine whether *all* fields of `params` are scalar values: strings, numbers, and options thereof
    scalars = [
        str,
        int,
        float,
        type(None),
        Optional[str],
        Optional[int],
        Optional[float],
    ]
    # Boolean indication of whether *all* param-datatypes are from among these
    all_scalar = all([param.dtype in scalars for param in params.__params__.values()])

    # If all params are scalars, create a readable string of their values
    if all_scalar:
        name = params.__class__.__name__ + "("
        for pname in params.__params__.keys():
            pval = getattr(params, pname)
            name += pname + "=" + str(pval) + " "
        name = name.rstrip()
        name += ")"

        # These names must also be limited in length, for sake of our favorite output formats.
        # If the generated name is too long, use the hashing method below instead
        if len(name) < 128:  # Probably(?) a reasonable length limit
            return name

    # Non-scalar cases generally include nested `@paramclasses` or sequences,
    # or surpass the length-limits above. We serialize and hash them.
    # Preferably serialize as JSON
    jsonstr = json.dumps(params, indent=4, default=hdl21_naming_encoder)
    data = bytes(jsonstr, encoding="utf-8")

    # If JSON encoding fails, we *could* use pickle instead.
    # Disabled for now, because pickle is not guaranteed to be deterministic.
    # Note JSON is preferable for its run-to-run stability,
    # where pickle can generally serialize more types.
    # data = pickle.dumps(params)

    # Take that data and hash it
    # Note the "not used for security" option ensures consistent hashing between runs/ Python-processes
    h = hashlib.new("md5", usedforsecurity=False)
    h.update(data)
    # Combine the `@paramclass` name with this (hex) digest
    return params.__class__.__name__ + "(" + h.hexdigest() + ")"


def hdl21_naming_encoder(obj: Any) -> Any:
    """ JSON encoder for naming of Hdl21 parameter-values. 

    "Extends" `pydantic.json.pydantic_encoder` by first checking for 
    each of the non-serializable Hdl21 types (`Module`, `Instance`, `Generator`, etc.), 
    then hands everything else off to `pydantic.json.pydantic_encoder`. 

    Note this *does not fully serialize `Module`s and the like - 
    see `hdl21.to_proto` for this. This JSON-ization is just good enough 
    to enable unique naming of Hdl-object-value parameters. """

    from .module import Module, ExternalModule, ExternalModuleCall
    from .instance import Instance
    from .generator import Generator, GeneratorCall

    if isinstance(obj, (Instance, Generator)):
        # Not supported as parameters
        raise RuntimeError(f"Invalid `hdl21.paramclass` field {obj}")
    if isinstance(obj, (Module, ExternalModule)):
        # Modules use their qualified class names/paths
        return obj._qualname()
    if isinstance(obj, ExternalModuleCall):
        # Mix the qualified class names/paths with the parameters
        return obj.module._qualname() + _unique_name(obj.params)
    if isinstance(obj, GeneratorCall):
        # Most other Hdl21 objects as parameters are pending, maybe, maybe not, support as parameter-values.
        raise NotImplementedError

    # Dataclasses also require custom handling, as the default encoder deep-copies them,
    # often invoking methods not supported on several Hdl21 types.
    # Convert to (shallow) dictionaries instead.
    if dataclasses.is_dataclass(obj):
        return {f.name: getattr(obj, f.name) for f in dataclasses.fields(obj)}

    # Not an Hdl21 type. Hand off to pydantic.
    return pydantic.json.pydantic_encoder(obj)


# Shortcut for parameter-less generators.
# Defines the empty-value `@paramclass`.
HasNoParams = paramclass(
    dataclasses.make_dataclass("NoParams", fields=[], namespace={}, frozen=True)
)
# And an instance of it
NoParams = HasNoParams()
