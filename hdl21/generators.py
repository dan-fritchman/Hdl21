""" 
# Hdl21 Built-In Generators Library 
"""

from copy import deepcopy
from typing import Tuple, Union

# This is about the one place within the library that we use the global, named import `hdl21 as h`,
# largely so that this module is a bit more copy-paste-edit-able.
import hdl21 as h


SeriesConn = Union[h.Signal, str]
SeriesConns = Tuple[SeriesConn, SeriesConn]


@h.paramclass
class SeriesParams:
    """# Series Generator Parameters"""

    # Required
    unit = h.Param(dtype=h.Instantiable, desc="Unit cell")
    conns = h.Param(dtype=SeriesConns, desc="Series ports (or names)")
    # Optional
    nser = h.Param(dtype=int, desc="Number in series", default=1)


@h.generator
def Series(params: SeriesParams) -> h.Module:
    """
    # Series Generator

    Arrays `params.nser` series-stacked Instances of unit-cell `params.unit`.
    The generated `Module` includes the same ports as `unit`.
    The two series-connected ports of `unit` are specified by parameter two-tuple `conns`.
    All other ports of `unit` are wired in parallel, and exposed as ports of the generated module.
    """

    if params.nser < 1:
        raise ValueError(f"Invalid Series() generator with nser={params.nser}")
    if params.nser == 1:
        return Wrapper(params.unit)  # Easy mode

    # Initialize our stack-module
    m = h.Module()

    # Copy the unit-cell ports
    for p in params.unit.ports.values():
        m.add(deepcopy(p))

    # Divy up the ports by series vs parallel connections
    series_conns = _seriesconns(m, params.conns)
    par_ports = [port for port in m.ports.values() if port not in series_conns]
    unit_conns = {port.name: port for port in par_ports}

    # Create the internal series-connected signals, and concatenate them with the series ports
    i = m.add(h.Signal(name="i", width=params.nser - 1))
    unit_conns[series_conns[0].name] = h.Concat(series_conns[0], i)
    unit_conns[series_conns[1].name] = h.Concat(i, series_conns[1])

    # Create an array of unit instances
    m.add(params.nser * params.unit(**unit_conns), name="units")

    # And return the module
    return m


def _seriesconns(m: h.Module, conns: SeriesConns) -> Tuple[h.Signal, h.Signal]:
    # Extract the signals specified by `SeriesConns`
    return (_seriesconn(m, conns[0]), _seriesconn(m, conns[1]))


def _seriesconn(m: h.Module, conn: SeriesConn) -> h.Signal:
    # Extract the signal specified by a `SeriesConn`
    if isinstance(conn, h.Signal):
        rv = m.ports.get(conn.name, None)
    elif isinstance(conn, str):
        rv = m.ports.get(conn, None)
    else:
        raise TypeError(f"Series: invalid series port {conn}")
    # Check that we got something, and that it's a Signal (not, e.g., a Bundle).
    if rv is None or not isinstance(rv, h.Signal):
        raise ValueError(f"Series: invalid series port {conn}")
    return rv


@h.paramclass
class MosStackParams:
    """# Mos Stack Parameters"""

    # All optional
    # Equal to `SeriesParams`, with:
    # - `conns` fixed to source/ drain
    # - `unit` has a default, the built-in `h.primitives.Mos`
    unit = h.Param(
        dtype=h.Instantiable, desc="Unit Mos cell", default_factory=h.primitives.Mos
    )
    nser = h.Param(dtype=int, desc="Number in series", default=1)


@h.generator
def MosStack(params: MosStackParams) -> h.Module:
    """# Mos Series-Stack Generator"""
    # Use the `Series` generator, with series-connections between drain and source.
    return Series(unit=params.unit, nser=params.nser, conns=("d", "s"))


def Wrapper(m: h.Instantiable) -> h.Module:
    """
    # Module Wrapper Creator

    Adds a `Module` hierarchy layer around argument-module (or other instantiable) `m`.
    Creates an `Instance` of `m` and clones its ports, connecting each.

    Note: `Wrapper` is generally aways more helpful when the returned `Module` is modified after the fact.
    Hence while `Wrapper` is a *function that returns a `Module`*, it is *not* an `hdl21.Generator`,
    which cache and unique-name their results.
    Callers of `Wrapper` are therefore responsible for considerations such as unique naming.
    """

    from .instantiable import io

    # Initialize our wrapper-module
    wrapper = h.Module(name=f"{m.name}Wrapper")

    # Copy the inner-cell ports
    # Note this also serves as the connections-dict to the inner instance
    wrapper_io = {p.name: wrapper.add(deepcopy(p)) for p in io(m).values()}

    # Create the inner instance
    wrapper.add(h.Instance(name="inner", of=m)(**wrapper_io))

    # And return the wrapper
    return wrapper


@h.paramclass
class AcDc:
    ac = h.Param(dtype=h.Prefixed, desc="AC Voltage", default=0)
    dc = h.Param(dtype=h.Prefixed, desc="DC Voltage", default=0)


@h.paramclass
class CmDmGenParams:
    cm = h.Param(dtype=AcDc, desc="Common-Mode Voltage", default_factory=AcDc)
    dm = h.Param(dtype=AcDc, desc="Differential Voltage", default_factory=AcDc)


@h.generator
def CmDmGen(p: CmDmGenParams) -> h.Module:
    """# Common & Differential Mode Generator"""

    @h.module
    class CmDmGen:
        # IO
        diff = h.Diff(port=True, role=h.Diff.Roles.SOURCE)
        VSS = h.Port()
        # Implementation
        vc = h.Vdc(dc=p.cm.dc, ac=p.cm.ac)(n=VSS)
        vp = h.Vdc(dc=p.dm.dc, ac=+p.dm.ac / 2)(p=diff.p, n=vc.p)
        vn = h.Vdc(dc=p.dm.dc, ac=-p.dm.ac / 2)(p=diff.n, n=vc.p)

    return CmDmGen


@h.generator
def Balun(_: h.HasNoParams) -> h.Module:
    """# Balun Generator"""

    @h.module
    class Balun:
        # IO
        vic = h.Diff(port=True, role=h.Diff.Roles.SINK)
        vid = h.Diff(port=True, role=h.Diff.Roles.SINK)
        vod = h.Diff(port=True, role=h.Diff.Roles.SOURCE)
        VSS = h.Ground()

        # Implementation
        voc = h.Signal()
        ec = h.Vcvs(gain=1)(p=voc, n=VSS, cp=vic.p, cn=vic.n)
        ep = h.Vcvs(gain=+500 * h.prefix.MILLI)(p=vod.p, n=voc, cp=vid.p, cn=vid.n)
        en = h.Vcvs(gain=-500 * h.prefix.MILLI)(p=vod.n, n=voc, cp=vid.p, cn=vid.n)

    return Balun
