"""
Hdl21 Parameters and Param-Classes 
"""

# Std-Lib Imports
import dataclasses, inspect, json, hashlib
from typing import Optional, Any, Type, TypeVar, Dict

# PyPi Imports
import pydantic

# Local Imports
from .default import Default

T = TypeVar("T")


def paramclass(cls: Type[T]) -> Type[T]:
    """# Parameter-Class Creation Decorator

    Transforms a class-definition full of Params into a type-validated dataclass,
    with methods for default value and description-dictionary retrieval.

    Hdl21's `paramclass`es are immutable, strongly-typed data-storage structures.
    They are defined through a syntax similar to `@dataclass`, but using the `Param`
    constructor, and assignment rather than type annotation.

    ```python
    @paramclass
    class C:
        reqd = Param(dtype=int, desc="A Required Parameter")
        optn = Param(dtype=int, desc="An Optional Parameter", default=11)
    ```

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

    if not inspect.isclass(cls):
        msg = f"Invalid @hdl21.paramclass `{cls}`. Apply the `@apramclass` decorator to classes."
        raise RuntimeError(msg)
    if cls.__bases__ != (object,):
        raise RuntimeError(f"Invalid @hdl21.paramclass inheriting from {cls.__bases__}")

    protected_names = ["descriptions", "defaults"]
    dunders = dict()  # Double-under attributes; ignored
    params = dict()  # Parameters; used to create dataclass fields

    # Take a lap through the class dictionary, type-check everything and grab Params
    # FIXME: look for, and alert users about, the error writing type annotations rather than equality.
    # (Or, we could move to type annotations...)
    for key, val in cls.__dict__.items():
        if key in protected_names:
            raise RuntimeError(f"Invalid field name {key} in paramclass {cls}")
        elif key.startswith("__"):
            dunders[key] = val
        elif isinstance(val, Param):
            params[key] = val
        else:
            msg = f"Invalid class-attribute {key} in paramclass {cls}. All attributes should be `hdl21.Param`s."
            raise RuntimeError(msg)

    # Set up type annotations for the dataclass-to-be
    # There is quite a bit of invaluable content on this here:
    # https://docs.python.org/3/howto/annotations.html
    # Especially for Python versions before 3.10.
    # Some of our constraints - notably the lack of inheritance, checked above -
    # make that advice somewhat easier to follow;
    # nonetheless we are definitely not following it in full.

    # Notably, this weird bit right here is the "howto/annotations" recommendation -
    # Look only in the class `__dict__`, and be prepared for `__annotations__` to be missing.
    annotations = cls.__dict__.get("__annotations__", None)
    if annotations is None:
        annotations = cls.__annotations__ = dict()

    # Translate the Params into dataclass-compatible annotations
    for name, param in params.items():
        # Set the type-annotation
        annotations[name] = param.dtype

        # Handle the default value, which is the class-attribute-value on dataclasses
        if param.default is not Default and param.default_factory is not Default:
            msg = f"Invalid Param {param} in paramclass {cls}. Only one of `default` or `default_factory` may be specified."
            raise RuntimeError(msg)

        elif param.default is not Default:
            setattr(cls, name, param.default)

        elif param.default_factory is not Default:
            field = dataclasses.field(default_factory=param.default_factory)
            setattr(cls, name, field)

        else:  # Otherwise there is no default value, this is a required parameter.
            # Remove the `Param` object from the class namespace
            delattr(cls, name)

    # Add a few helpers to the class namespace
    cls.__params__ = params
    cls.__paramclass__ = True
    cls.descriptions = classmethod(descriptions)
    cls.defaults = classmethod(defaults)

    # Pass this through the pydantic dataclass-decorator-function
    cls = pydantic.dataclasses.dataclass(cls, config=Config, frozen=True)

    # Pydantic seems to want to add this one *after* class-creation
    def _brick_subclassing_(cls, *_, **__):
        msg = f"Error: attempt to sub-class `hdl21.paramclass` {cls} is not supported"
        raise RuntimeError(msg)

    cls.__init_subclass__ = classmethod(_brick_subclassing_)
    # And don't forget to return it!
    return cls


def descriptions(cls: Type) -> Dict[str, str]:
    """# Get a dictionary of parameter names to descriptions for `cls`
    Available both as a free function and as a `classmethod` of each `paramclass`.
    Raises a `RuntimeError` if `cls` is not a param-class."""

    if not isparamclass(cls):
        raise RuntimeError(f"Invalid @hdl21.paramclass {cls}")

    return {k: v.desc for k, v in cls.__params__.items()}


def defaults(cls: Type) -> Dict[str, Any]:
    """# Get a dictionary of parameter names to default values for param-class `cls`.
    Available both as a free function and as a `classmethod` of each `paramclass`.
    Raises a `RuntimeError` if `cls` is not a param-class."""

    if not isparamclass(cls):
        raise RuntimeError(f"Invalid @hdl21.paramclass {cls}")

    return {k: v.default for k, v in cls.__params__.items() if v.default is not Default}


def isparamclass(cls: type) -> bool:
    """Boolean indication of whether `cls` has been `@paramclass`-decorated"""
    return getattr(cls, "__paramclass__", False)


class Config:  # Pydantic Model Config
    allow_extra = pydantic.Extra.forbid


@pydantic.dataclasses.dataclass(config=Config, frozen=True)
class Param:
    """# Parameter Declaration"""

    dtype: Any  # Datatype. Required
    desc: str  # Description. Required
    default: Optional[Any] = Default  # Default Value. Optional
    default_factory: Optional[Any] = Default  # Default Call-Factory. Optional


def _unique_name(params: Any) -> str:
    """Create a unique name for parameter-class instance `params`"""
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
        # Format: `pname1=pval1 pname2=pval2 pname3=pval3`
        keys = params.__params__.keys()
        name = " ".join(f"{k}={str(getattr(params, k))}" for k in keys)

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
    # And return the (hex) digest as our unique name
    return h.hexdigest()


def hdl21_naming_encoder(obj: Any) -> Any:
    """JSON encoder for naming of Hdl21 parameter-values.

    "Extends" `pydantic.json.pydantic_encoder` by first checking for
    each of the non-serializable Hdl21 types (`Module`, `Instance`, `Generator`, etc.),
    then hands everything else off to `pydantic.json.pydantic_encoder`.

    Note this *does not fully serialize `Module`s and the like -
    see `hdl21.to_proto` for this. This JSON-ization is just good enough
    to enable unique naming of Hdl-object-valued parameters."""

    from .module import Module
    from .qualname import qualname as module_qualname
    from .external_module import ExternalModule, ExternalModuleCall
    from .instance import Instance
    from .generator import Generator, GeneratorCall
    from .primitives import Primitive, PrimitiveCall

    if isinstance(obj, (Instance,)):
        # Not supported as parameters
        raise RuntimeError(f"Invalid `hdl21.paramclass` field {obj}")

    if isinstance(obj, (Module, ExternalModule, Generator)):
        # Use qualified class names/paths
        return module_qualname(obj)

    if isinstance(obj, (Primitive, PrimitiveCall)):
        # Primitives use their `name` attribute/ property directly
        return obj.name

    # Mix the qualified class names/paths with the parameters
    if isinstance(obj, GeneratorCall):
        return module_qualname(obj.gen) + _unique_name(obj.params)

    if isinstance(obj, ExternalModuleCall):
        # Mix the qualified class names/paths with the parameters
        return module_qualname(obj.module) + _unique_name(obj.params)

    # Dataclasses also require custom handling, as the default encoder deep-copies them,
    # often invoking methods not supported on several Hdl21 types.
    # Convert to (shallow) dictionaries instead.
    if dataclasses.is_dataclass(obj):
        return {f.name: getattr(obj, f.name) for f in dataclasses.fields(obj)}

    # Not an Hdl21 type. Hand off to pydantic.
    return pydantic.json.pydantic_encoder(obj)


# Shortcut for parameter-less generators.
# Defines the empty-value `@paramclass`.
@paramclass
class HasNoParams:
    """# HasNoParams
    A built-in `hdl21.paramclass` for generators that require no parameters."""

    ...  # Empty Contents


# And an instance of it
NoParams = HasNoParams()

__all__ = ["paramclass", "Param", "HasNoParams", "NoParams"]
