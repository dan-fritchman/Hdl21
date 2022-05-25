"""
# VLSIR ProtoBuf Schema Export
"""

# Std-Lib Imports
from typing import List, Union
from decimal import Decimal

# VLSIR Import
import vlsir
import vlsir.spice_pb2 as vsp

# Local Imports
from . import data
from ..prefix import Prefixed
from ..signal import Signal


def to_proto(sim: data.Sim) -> vsp.SimInput:
    """ Convert a `Sim` to a VLSIR `SimInput` """
    exporter = ProtoExporter(sim=sim)
    return exporter.export()


class ProtoExporter:
    """ Simulation Protobuf Exporter """

    def __init__(self, sim: data.Sim):
        self.sim = sim  # Store the input `Sim`
        self.inp = None  # Initialize our resultant `vsp.SimInput`

    def export(self) -> vsp.SimInput:
        """ Primary export method. Converts `sim.tb` and its dependencies to a `Package`, 
        and all other `SimAttr`s to VLSIR attributes. """
        from ..proto import to_proto as module_to_proto
        from ..instantiable import qualname

        # Convert the testbench module and all its dependencies into a `Package`
        pkg = module_to_proto(self.sim.tb)

        # Now that the testbench has been elaborated, ensure it adheres to the testbench interface.
        if not data.is_tb(self.sim.tb):
            raise RuntimeError(f"Invalid Testbench {self.sim.tb} for Simulation")

        # Create our `SimInput`, and provide it with a "link" to the testbench, via its name
        self.inp = vsp.SimInput(pkg=pkg, top=qualname(self.sim.tb))

        # Export each simulation attribute
        for attr in self.sim.attrs:
            self.export_attr(attr)
        return self.inp

    def export_attr(self, attr: data.SimAttr) -> None:
        """ Export a Sim Attribute. Primarily dispatches across internal union-types. """
        from .data import is_analysis, is_control

        if isinstance(attr, data.Options):
            self.inp.opts.append(export_options(attr))
        elif is_analysis(attr):
            self.inp.an.append(self.export_analysis(attr))
        elif is_control(attr):
            self.inp.ctrls.append(export_control(attr))
        else:
            raise TypeError(f"Invalid SimAttr: {attr}")

    def export_analysis(self, an: data.Analysis) -> vsp.Analysis:
        """ Export an `Analysis`, largely dispatching across types and re-assembling into a `vsp.Analysis`. """
        if isinstance(an, data.Dc):
            return vsp.Analysis(dc=self.export_dc(an))
        elif isinstance(an, data.Ac):
            return vsp.Analysis(ac=self.export_ac(an))
        elif isinstance(an, data.Tran):
            return vsp.Analysis(tran=self.export_tran(an))
        elif isinstance(an, data.SweepAnalysis):
            return vsp.Analysis(sweep=self.export_sweep_analysis(an))
        elif isinstance(an, data.MonteCarlo):
            return vsp.Analysis(monte=self.export_monte(an))
        elif isinstance(an, data.CustomAnalysis):
            return vsp.Analysis(custom=self.export_custom_analysis(an))
        else:
            raise TypeError(f"Invalid Analysis {an}")

    def export_dc(self, dc: data.Dc) -> vsp.DcInput:
        """ Export a DC analysis """
        return vsp.DcInput(
            analysis_name=dc.name,
            indep_name=self.export_sweep_variable(dc.var),
            sweep=self.export_sweep(dc.sweep),
            ctrls=[],  # FIXME: analysis-specific controls
        )

    def export_ac(self, ac: data.Ac) -> vsp.AcInput:
        """ Export an AC analysis """
        return vsp.AcInput(
            analysis_name=ac.name,
            fstart=ac.sweep.start,
            fstop=ac.sweep.stop,
            npts=ac.sweep.npts,
            ctrls=[],  # FIXME: analysis-specific controls
        )

    def export_tran(self, tran: data.Tran) -> vsp.TranInput:
        """ Export a transient analysis """
        return vsp.TranInput(
            analysis_name=tran.name,
            tstop=tran.tstop,
            tstep=tran.tstep,
            ic={},  # FIXME: initial conditions
            ctrls=[],  # FIXME: analysis-specific controls
        )

    def export_sweep_analysis(self, swp_an: data.SweepAnalysis) -> vsp.SweepInput:
        """ Export a swept, nested set of one or more inner analyses as a `SweepInput`. """
        return vsp.SweepInput(
            analysis_name=swp_an.name,
            variable=self.export_sweep_variable(swp_an.var),
            sweep=self.export_sweep(swp_an.sweep),
            an=[self.export_analysis(a) for a in swp_an.inner],
            ctrls=[],  # FIXME: analysis-specific controls
        )

    def export_monte(self, monte: data.MonteCarlo) -> vsp.MonteInput:
        """ Export a monte-carlo analysis """
        return vsp.MonteInput(
            analysis_name=monte.name,
            npts=monte.npts,
            seed=0,  # FIXME: programmable seeds?
            an=[self.export_analysis(a) for a in monte.inner],
            ctrls=[],  # FIXME: analysis-specific controls
        )

    def export_custom_analysis(
        self, an: data.CustomAnalysis
    ) -> vsp.CustomAnalysisInput:
        """ Export a custom analysis """
        raise NotImplementedError

    def export_sweep_variable(self, var: Union[str, data.Param]) -> str:
        """ Export a sweep-variable to its name. """
        if isinstance(var, str):
            return var
        elif isinstance(var, data.Param):
            return var.name
        raise TypeError(f"Invalid sweep variable {var}")

    def export_sweep(self, sweep: data.Sweep) -> vsp.Sweep:
        """ Export a data sweep. """
        if isinstance(sweep, data.LinearSweep):
            return vsp.Sweep(
                linear=vsp.LinearSweep(
                    start=export_float(sweep.start),
                    stop=export_float(sweep.stop),
                    step=export_float(sweep.step),
                )
            )
        elif isinstance(sweep, data.LogSweep):
            return vsp.Sweep(
                log=vsp.LogSweep(
                    start=export_float(sweep.start),
                    stop=export_float(sweep.stop),
                    npts=export_float(sweep.npts),  # FIXME: move to int
                )
            )
        elif isinstance(sweep, data.PointSweep):
            return vsp.Sweep(
                points=vsp.PointSweep(points=[export_float(x) for x in sweep.points])
            )
        else:
            raise TypeError(f"Invalid Sweep value {sweep}")


def export_options(options: data.Options) -> vsp.SimOptions:
    """ Export simulation options """
    return vsp.SimOptions(
        temp=options.temper,
        tnom=options.tnom,
        gmin=options.gmin,
        iabstol=options.iabstol,
        reltol=options.reltol,
    )


def export_control(ctrl: data.Control) -> vsp.Control:
    """ Export a `Control` element """
    if isinstance(ctrl, data.Include):
        return vsp.Control(include=export_include(ctrl))
    if isinstance(ctrl, data.Lib):
        return vsp.Control(lib=export_lib(ctrl))
    if isinstance(ctrl, data.Save):
        return vsp.Control(save=export_save(ctrl))
    if isinstance(ctrl, data.Meas):
        return vsp.Control(meas=export_meas(ctrl))
    if isinstance(ctrl, data.Param):
        return vsp.Control(param=export_param(ctrl))
    if isinstance(ctrl, data.Literal):
        return vsp.Control(literal=export_literal(ctrl))
    raise TypeError(f"Invalid Sim Control {ctrl}")


def export_include(inc: data.Include) -> vsp.Include:
    return vsp.Include(path=str(inc.path))


def export_lib(lib: data.Lib) -> vsp.LibInclude:
    return vsp.LibInclude(path=str(lib.path), section=lib.section)


def export_save(save: data.Save) -> vsp.Save:
    if isinstance(save.targ, data.SaveMode):
        if save.targ == data.SaveMode.ALL:
            mode = vsp.Save.SaveMode.ALL
        elif save.targ == data.SaveMode.NONE:
            mode = vsp.Save.SaveMode.NONE
        else:
            raise ValueError
        return vsp.Save(mode=mode)
    if isinstance(save.targ, Signal):
        signal = save.targ.name
    elif isinstance(save.targ, List[Signal]):
        signal = ",".join([s.name for s in save.targ])
    elif isinstance(save.targ, str):
        signal = save.targ
    elif isinstance(save.targ, List[str]):
        signal = ",".join([s for s in save.targ])
    else:
        raise TypeError
    return vsp.Save(signal=signal)


def export_meas(meas: data.Meas) -> vsp.Meas:
    """ Export a measurement """
    return vsp.Meas(
        analysis_type=export_analysis_type(meas.analysis),
        name=meas.name,
        expr=str(meas.expr),
    )


def export_analysis_type(an: Union[str, data.Analysis]) -> str:
    """ Export an `AnalysisType`, or string representation thereof. """
    if isinstance(an, str):
        return an
    if data.is_analysis(an):
        return an.tp.value
    raise TypeError(f"Invalid Analysis for type-extraction {an}")


def export_param(param: data.Param) -> vlsir.Param:
    """ Export a parameter declaration """
    from ..proto.to_proto import export_param_value

    return vlsir.Param(name=param.name, value=export_param_value(param.val))


def export_literal(literal: data.Literal) -> str:
    """ Export a simulation literal, as its text value """
    return literal.txt


def export_float(num: Union[float, int, Decimal, Prefixed]) -> float:
    """ Export a `Number` union-type to a float, or protobuf float/double. """
    if isinstance(num, float):
        return num
    if isinstance(num, (int, Decimal, Prefixed)):
        return float(num)
    raise TypeError(f"Invalid value for proto float: {num}")
