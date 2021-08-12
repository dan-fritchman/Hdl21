from . import compile
import hdl21 as h


def test1():
    # Create a simple Module with each of the default-param Mos types
    hasmos = h.Module(name="hasmos")
    hasmos.n = h.Nmos(h.MosParams())()
    hasmos.p = h.Pmos(h.MosParams())()

    # Compile it for the PDK
    pkg = h.to_proto(hasmos)
    compiled = compile(pkg)
    ns = h.from_proto(compiled)
    print(dir(ns))
    print(3)
    print(compiled)
