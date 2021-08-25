"""
Hdl21 Parameters and Param-Classes 
"""

from typing import Optional, Any
import dataclasses
import hashlib
import pickle
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


def paramclass(cls: type):
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

    # Note the "not used for security" option ensures consistent hashing between runs/ Python-processes
    h = hashlib.new("md5", usedforsecurity=False)
    # We will pickle the params object to serialize it and hash it
    h.update(pickle.dumps(params))
    # Combine the `@paramclass` name with this (hex) digest
    return params.__class__.__name__ + "(" + h.hexdigest() + ")"


# Shortcut for parameter-less generators.
# Defines the empty-value `@paramclass`.
HasNoParams = paramclass(
    dataclasses.make_dataclass("NoParams", fields=[], namespace={}, frozen=True)
)
# And an instance of it
NoParams = HasNoParams()
