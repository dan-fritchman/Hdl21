import inspect
from dataclasses import dataclass
from .module import Module


@dataclass
class Generator:
    func: object
    paramtype: type


def generator(f):
    """ Decorator for Generator Functions """
    if not callable(f):
        raise RuntimeError
    sig = inspect.signature(f)

    return Generator(func=f, paramtype=None)


class Context:
    ...


class Elaborator:
    def __init__(
        self, *, top: Generator, params: object, ctx: Context,
    ):
        self.top = top
        self.ctx = ctx
        self.params = params

    def elaborate(self) -> Module:
        return self.elaborate_generator(self.top, self.params)

    def elaborate_generator(self, gen: Generator, params: object) -> Module:
        # FIXME: all sorts of manipulating whether to send context, conver types, etc.
        m = gen.func(params)
        m._genparams = params
        # If the Module that comes back is anonymous, give it a name equal to the Generator's
        if m.name is None:
            m.name = gen.func.__name__
        return m


def elaborate(top: Generator, params=None, ctx=None):
    ctx = ctx or Context()
    if params is not None and not isinstance(top, Generator):
        raise RuntimeError(
            f"Error attempting to elaborate non-generator {top} with non-null params {params}"
        )
    elab = Elaborator(top=top, params=params, ctx=ctx)
    return elab.elaborate()

