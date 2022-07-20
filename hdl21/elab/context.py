"""
# Elaboration Context 

Cross-hierarchy contextual information exposed to `hdl21.Generator`s during elaboration. 
The most common use for the elaboration Context is passing information deep through design hierarchies 
without explicitly needing to pipe it through each layer. 
This proves particularly invaluable if lower layers are designed to be swapped in or out, 
e.g. through the importing of different implementations. 

An example of using the context to access elaboration-wide power and ground signals `VDD` and `VSS`: 

```python
@h.generator
def HasPwrGnd(_: h.HasNoParams, ctx: Context) -> h.Module:
    m = h.Module()
    m.VDD, m.VSS = ctx.pwrgnd()
    return m
```

And for an elaboration-wide clock-signal `clk`:

```python
@h.generator
def HasClk(_: h.HasNoParams, ctx: Context) -> h.Module:
    m = h.Module()
    m.clk = ctx.clk()
    return m
```


"""

# Std-Lib Imports
from enum import Enum, auto
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

# Local Imports
from ..signal import Signal


class ContextUseType(Enum):
    """Enumerated Types of Context Usages"""

    PWR = auto()
    GND = auto()
    CLK = auto()


@dataclass
class ContextUsage:
    """Context Usage"""

    call: "GeneratorCall"
    tp: ContextUseType
    signal: Signal


@dataclass
class ElabSession:
    """# Elaboration Session"""

    current: Optional["GeneratorCall"] = None
    elaborator: Optional["Elaborator"] = None
    usages: List[ContextUsage] = field(default_factory=list)


class Context:
    """# Elaboration Context"""

    session: Optional[ElabSession] = None

    supplies: List[Signal] = field(default_factory=lambda _: [Signal(name="VDD")])
    grounds: List[Signal] = field(default_factory=lambda _: [Signal(name="VSS")])
    clocks: List[Signal] = field(default_factory=lambda _: [Signal(name="clk")])

    def mark(self, tp: ContextUseType, signal: Signal) -> None:
        """Mark a usage of the Context"""
        if self.session.current is None:
            msg = "Invalid `Context.use` outside of `Generator`!"
            self.session.elaborator.fail(msg)
        # Mark that we've used the Context here
        usage = ContextUsage(call=self.session.current, tp=tp, signal=signal)
        self.session.usages.append(usage)

    def pwrgnd(self) -> Tuple[Signal, Signal]:
        """Get Power and Ground `Signal`s.
        Raises an Exception if the Context is configured for more than one Power or Ground.
        Equivalent to back-to-back calls to `pwr()` and `gnd()`."""
        return self.pwr(), self.gnd()

    def pwr(self) -> Signal:
        """Get Power `Signal`"""
        if len(self.supplies) != 1:
            msg = "Invalid `Context.pwr`: multiple supplies"
            self.session.elaborator.fail(msg)
        self.mark(ContextUseType.PWR, self.supplies[0])
        return self.supplies[0]

    def gnd(self) -> Signal:
        """Get Ground `Signal`"""
        if len(self.grounds) != 1:
            msg = "Invalid `Context.gnd`: multiple grounds"
            self.session.elaborator.fail(msg)

        self.mark(ContextUseType.GND, self.grounds[0])
        return self.grounds[0]

    def clk(self) -> Signal:
        """Get Clock `Signal`"""
        if len(self.clks) != 1:
            msg = "Invalid `Context.clk`: multiple clocks"
            self.session.elaborator.fail(msg)

        self.mark(ContextUseType.CLK, self.clocks[0])
        return self.grounds[0]
