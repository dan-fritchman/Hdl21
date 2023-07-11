# HDL21

## Analog Hardware Description Library in Python

[![pypi](https://img.shields.io/badge/pypi-hdl21-blue)](https://pypi.org/project/hdl21/)
[![python-versions](https://img.shields.io/badge/python-3.7_3.8_3.9_3.10_3.11-blue)](https://codecov.io/gh/dan-fritchman/Hdl21)
[![test](https://github.com/dan-fritchman/Hdl21/actions/workflows/test.yaml/badge.svg)](https://github.com/dan-fritchman/Hdl21/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/dan-fritchman/Hdl21/branch/main/graph/badge.svg?token=f8LKUqEPdq)](https://codecov.io/gh/dan-fritchman/Hdl21)

Hdl21 is a [hardware description library](https://en.wikipedia.org/wiki/Hardware_description_language) embedded in Python.  
It is targeted for analog and custom integrated circuits, and for maximum productivity with minimum fancy-programming skill.

## Contents

- [Installation](#installation)
- [Modules](#modules)
- [Signals](#signals), [Ports](#signals), and [Connections](#connections)
- [Generators](#generators) and [Parameters](#parameters)
- [Primitive Elements and External Modules](#primitives-and-external-modules)
- [Spice-Class Simulation](#spice-class-simulation)
- [Process Technologies (PDKs)](#process-technologies)
- [Bundles](#bundles)
- [Examples](#examples)
- [Related Projects](#related-projects)

## Installation

```
pip install hdl21
```

That's it. No crazy build step, no crazy dependencies, no crazy EDA stuff, no "clone and _just_ modify these 300 things", no `source`ing, none of that. Hdl21 is pure Python, and is designed to be as easy to install as any other Python package.

## Modules

Hdl21's primary unit of hardware reuse is the `Module`. Think of it as Verilog's `module`, or VHDL's `entity`, or SPICE's `subckt`. Better yet if you are used to graphical schematics, think of it as the content of a schematic. Hdl21 `Modules` are containers of a handful of `hdl21` types. Think of them as including:

- Instances of other `Modules`
- Connections between them, defined by `Signals` and `Ports`
- Fancy combinations thereof, covered later

An example `Module`:

```python
import hdl21 as h

m = h.Module(name="MyModule")
m.i = h.Input()
m.o = h.Output(width=8)
m.s = h.Signal()
m.a = AnotherModule()
```

In addition to the procedural-syntax shown above, `Modules` can also be defined through a `class`-based syntax by applying the `hdl21.module` decorator to a class-definition.

```python
import hdl21 as h

@h.module
class MyModule:
    i = h.Input()
    o = h.Output(width=8)
    s = h.Signal()
    a = AnotherModule()
```

This class-based syntax produces identical results to the procedural code-block above. Its declarative style can be much more natural and expressive in many contexts, especially for designers familiar with popular HDLs.

Creation of `Module` signal-attributes is generally performed by the built-in `Signal`, `Port`, `Input`, and `Output` constructors. Each comes with a "plural version" (`Input*s*` etc.) which creates several identical objects at once:

```python
import hdl21 as h

@h.module
class MyModule:
    a, b = h.Inputs(2)
    c, d, e = h.Outputs(3, width=16)
    z, y, x, w = h.Signals(4)
```

## Signals

Hdl21's primary connection type is `Signal`. Think of it as Verilog's `wire`, or a node in that schematic. Each `Signal` has an integer-valued bus `width` field, and can be connected to any other equal-width `Port`.

A subset of `Signals` are exposed outside their parent `Module`. These externally-connectable signals are referred to as `Ports`. Hdl21 provides four port constructors: `Input`, `Output`, `Inout`, and `Port`. The last creates a directionless (or direction unspecified) port akin to those of common spice-level languages.

## Connections

Popular HDLs generally feature one of two forms of connection semantics. Verilog, VHDL, and most dedicated HDLs use "connect by call" semantics, in which signal-objects are first declared, then passed as function-call-style arguments to instances of other modules.

```verilog
module my_module();
  logic a, b, c;                              // Declare signals
  another_module i1 (a, b, c);                // Create an instance
  another_module i2 (.a(a), .b(b), .c(c));    // Another instance, connected by-name
endmodule
```

Chisel, in contrast, uses "connection by assignment" - more literally using the walrus `:=` operator. Instances of child modules are created first, and their ports are directly walrus-connected to one another. No local-signal objects ever need be declared in the instantiating parent module.

```scala
class MyModule extends Module {
  // Create Module Instances
  val i1 = Module(new AnotherModule)
  val i2 = Module(new AnotherModule)
  // Wire them directly to one another
  i1.io.a := i2.io.a
  i1.io.b := i2.io.b
  i1.io.c := i2.io.c
}
```

Each can be more concise and expressive depending on context. Hdl21 `Modules` support **both** connect-by-call and connect-by-assignment forms.

Connections by assignment are performed by assigning either a `Signal` or another instance's `Port` to an attribute of a Module-Instance.

```python
# Create a module
m = h.Module()
# Create its internal Signals
m.a, m.b, m.c = h.Signals(3)
# Create an Instance
m.i1 = AnotherModule()
# And wire them up
m.i1.a = m.a
m.i1.b = m.b
m.i1.c = m.c
```

This also works without the parent-module `Signals`:

```python
# Create a module
m = h.Module()
# Create the Instances
m.i1 = AnotherModule()
m.i2 = AnotherModule()
# And wire them up
m.i1.a = m.i2.a
m.i1.b = m.i2.b
m.i1.c = m.i2.c
```

Instances can instead be connected by call:

```python
# Create a module
m = h.Module()
# Create the Instances
m.i1 = AnotherModule()
m.i2 = AnotherModule()
# Call one to connect them
m.i1(a=m.i2.a, b=m.i2.b, c=m.i2.c)
```

These connection-calls can also be performed inline, as the instances are being created.

```python
# Create a module
m = h.Module()
# Create the Instance `i1`
m.i1 = AnotherModule()
# Create another Instance `i2`, and connect to `i1`
m.i2 = AnotherModule(a=m.i1.a, b=m.i1.b, c=m.i1.c)
```

## Generators

Hdl21 `Modules` are "plain old data". They require no runtime or execution environment. They can be (and are!) fully represented in markup languages such as ProtoBuf, JSON, and YAML. The power of embedding `Modules` in a general-purpose programming language lies in allowing code to create and manipulate them. Hdl21's `Generators` are functions which produce `Modules`, and have a number of built-in features to aid embedding in a hierarchical hardware tree.

In other words:

- `Modules` are "structs". `Generator`s are _functions_ which return `Modules`.
- `Generators` are code. `Modules` are data.
- `Generators` require a runtime environment. `Modules` do not.

Creating a generator just requires applying the `@hdl21.generator` decorator to a Python function:

```python
import hdl21 as h

@h.generator
def MyFirstGenerator(params: MyParams) -> h.Module:
    # A very exciting first generator function
    m = h.Module()
    m.i = h.Input(width=params.w)
    return m
```

The generator-function body can define a `Module` however it likes - procedurally or via the class-style syntax.

```python
@h.generator
def MySecondGenerator(params: MyParams) -> h.Module:
    # A very exciting (second) generator function
    @h.module
    class MySecondGen:
        i = h.Input(width=params.w)
    return MySecondGen
```

Or any combination of the two:

```python
@h.generator
def MyThirdGenerator(params: MyParams) -> h.Module:
    # Create an internal Module
    @h.module
    class Inner:
        i = h.Input(width=params.w)

    # Manipulate it a bit
    Inner.o = h.Output(width=2 * Inner.i.width)

    # Instantiate that in another Module
    @h.module
    class Outer:
        inner = Inner()

    # And manipulate that some more too
    Outer.inp = h.Input(width=params.w)
    return Outer
```

## Parameters

`Generators` must take a single argument `params` which is a collection of `hdl21.Params`. Generator parameters are strongly type-checked at runtime. Each requires a data-type `dtype` and description-string `desc`. Optional parameters include a default-value, which must be an instance of `dtype`.

```python
# Example parameter:
npar = h.Param(dtype=int, desc="Number of parallel fingers", default=1)
```

The collections of these parameters used by `Generators` are called param-classes, and are typically formed by applying the `hdl21.paramclass` decorator to a class-body-full of `hdl21.Params`:

```python
import hdl21 as h

@h.paramclass
class MyParams:
    # Required
    width = h.Param(dtype=int, desc="Width. Required")
    # Optional - including a default value
    text = h.Param(dtype=str, desc="Optional string", default="My Favorite Module")
```

Each param-class is defined similarly to the Python standard-library's `dataclass`. The `paramclass` decorator converts these class-definitions into type-checked `dataclasses`, with fields using the `dtype` of each parameter.

```python
p = MyParams(width=8, text="Your Favorite Module")
assert p.width == 8  # Passes. Note this is an `int`, not a `Param`
assert p.text == "Your Favorite Module"  # Also passes
```

Similar to `dataclasses`, param-class constructors use the field-order defined in the class body. Note Python's function-argument rules dictate that all required arguments be declared first, and all optional arguments come last.

Param-classes can be nested, and can be converted to (potentially nested) dictionaries via `dataclasses.asdict`. The same conversion applies in reverse - (potentially nested) dictionaries can be expanded to serve as param-class constructor arguments:

```python
import hdl21 as h
from dataclasses import asdict

@h.paramclass
class Inner:
    i = h.Param(dtype=int, desc="Inner int-field")

@h.paramclass
class Outer:
    inner = h.Param(dtype=Inner, desc="Inner fields")
    f = h.Param(dtype=float, desc="A float", default=3.14159)

# Create from a (nested) dictionary literal
d1 = {"inner": {"i": 11}, "f": 22.2}
o = Outer(**d1)
# Convert back to another dictionary
d2 = asdict(o)
# And check they line up
assert d1 == d2
```

Generators include the capability to construct their param-classes inline, if provided a set of compatible keyword arguments. For example, defining a generator using the `MyParams` parameters above:

```python
@h.generator
def MyGen(params: MyParams) -> h.Module:
    ... # Create a `Module` & return it
```

This typical invocation:

```python
p = MyParams(width=8, text="My Favorite Module")
MyGen(p)
```

is the same as calling:

```python
MyParams(width=8, text="My Favorite Module")
```

Parameters may be provided as keywords, or as a single positional argument which is an instance of the generator's param-class. Combinations of the two are not supported.

## A Note on Parametrization

Hdl21 `Generators` have parameters. `Modules` do not.

This is a deliberate decision, which in this sense makes `hdl21.Module` less feature-rich than the analogous `module` concepts in existing HDLs (Verilog, VHDL, and even SPICE). These languages support what might be called "static parameters" - relatively simple relationships between parent and child-module parameterization. Setting, for example, the width of a signal or number of instances in an array is straightforward. But more elaborate parametrization-cases are either highly cumbersome or altogether impossible to create. (As an example, try using Verilog parametrization to make a programmable-depth binary tree.) Hdl21, in contrast, exposes all parametrization to the full Python-power of its generators.

## Numeric Parameters

### `Prefixed` Numbers

Hdl21 provides an [SI prefixed](https://www.nist.gov/pml/owm/metric-si-prefixes) numeric type `Prefixed`, which is especially common for physical generator parameters. Each `Prefixed` value is a combination of the Python standard library's `Decimal` and an enumerated SI `Prefix`:

```python
@dataclass
class Prefixed:
    number: Decimal  # Numeric Portion
    prefix: Prefix   # Enumerated SI Prefix
```

Most of Hdl21's built-in `Generators` and `Primitives` use `Prefixed` extensively, for a key reason: floating-point rounding. It is commonplace for physical parameter values - e.g. the physical width of a transistor - to have _allowed_ and _disallowed_ values. And those values do not necessarily land on IEEE floating-point values! Hdl21 generators are often used to produce legacy-HDL netlists and other code, which must convert these values to strings. `Prefixed` ensures a way to do this at arbitrary scale without the possibility of rounding error.

`Prefixed` values rarely need to be instantiated directly. Instead Hdl21 exposes a set of common prefixes via their typical single-character names:

```python
f = FEMTO = Prefix.FEMTO
p = PICO = Prefix.PICO
n = NANO = Prefix.NANO
µ = u = MICRO = Prefix.MICRO # Note both `u` and `µ` are valid
m = MILLI = Prefix.MILLI
K = KILO = Prefix.KILO
M = MEGA = Prefix.MEGA
G = GIGA = Prefix.GIGA
T = TERA = Prefix.TERA
P = PETA = Prefix.PETA
UNIT = Prefix.UNIT
```

Multiplying by these values produces a `Prefixed` value.

```python
from hdl21.prefix import µ, n, f

# Create a few parameter values using them
Mos.Params(
    w=1 * µ,
    l=20 * n,
)
Capacitor.Params(
    c=1 * f,
)
```

These multiplications are the easiest and most common way to create `Prefixed` parameter values.
Note the single-character identifiers `µ`, `n`, `f`, et al _are not_ exported by star-exports (`from hdl21 import *`). They must be imported explicitly from `hdl21.prefix`.

`hdl21.prefix` also exposes an `e()` function, which produces a prefix from an integer exponent value:

```python
from hdl21.prefix import e, µ

11 * e(-6) == 11 * µ  # True
```

These `e()` values are also most common in multiplication expressions,
to create `Prefixed` values in "floating point" style such as `11 * e(-9)`.

### `Scalar`

Many Hdl21 primitive parameters can be either numbers or string-literals.  
The combination is so common that Hdl21 defines a `Scalar` type which is (roughly):

```python
Scalar = Union[Prefixed, Literal]
```

With automatic conversions from each of `str`, `int`, `float`, and `Decimal`.

`Scalar` is particularly designed for parameter-values of `Primitive`s and of simulations.
Most such parameters "want" to be the `Prefixed` type, for reasons outlined [above](#prefixed-numeric-parameters). They often also need a string-valued escape hatch, e.g. when referring to out-of-Hdl21 quantities
such as parameters in external netlists or simulation decks.
These out-of-Hdl21 expressions are represented by the `Literal` type, a simple wrapper around `str`.

Where possible `Scalar` prefers to use the `Prefixed` variant.
Built-in numbers `(int, float, Decimal)` are converted to `Prefixed` inline.
Strings are attempted to be converted to `Prefixed`, and fall back to `Literal` if unsuccessful.
This conversion process is also available as the free-standing `to_scalar()` function.

Example:

```python
import hdl21 as h
from hdl21.prefix import NANO, µ
from decimal import Decimal

@h.paramclass
class MyMosParams:
    w = h.Param(dtype=h.Scalar, desc="Width", default=1e-6) # Default `float` converts to a `Prefixed`
    l = h.Param(dtype=h.Scalar, desc="Length", default="w/5") # Default `str` converts to a `Literal`

# Example instantiations
MyMosParams() # Default values
MyMosParams(w=Decimal(1e-6), l=3*µ)
MyMosParams(w=h.Literal("sim_param_width"), l=h.Prefixed.new(20, NANO))
MyMosParams(w="11*l", l=11)
```

When defining "primitive level" parameters - e.g. those that will be used in PDK-level devices - `Scalar` is generally the best datatype to use.

## Primitives and External Modules

The leaf-nodes of each hierarchical Hdl21 circuit are generally defined in one of two places:

- `Primitive` elements, defined in the `hdl21.primitives` package. Each is designed to be a technology-independent representation of an irreducible component.
- `ExternalModules`, defined outside Hdl21. Such "module wrappers", which might alternately be called "black boxes", are common for including circuits from other HDLs.

### `Primitives`

Hdl21's library of generic primitive elements is defined in the `hdl21.primitives` package. Its content is roughly equivalent to that built into a typical SPICE simulator.

A summary of `hdl21.primitives`:

| Name                           | Description                       | Type     | Aliases                               | Ports        |
| ------------------------------ | --------------------------------- | -------- | ------------------------------------- | ------------ |
| Mos                            | Mos Transistor                    | PHYSICAL | MOS                                   | d, g, s, b   |
| IdealResistor                  | Ideal Resistor                    | IDEAL    | R, Res, Resistor, IdealR, IdealRes    | p, n         |
| PhysicalResistor               | Physical Resistor                 | PHYSICAL | PhyR, PhyRes, ResPhy, PhyResistor     | p, n         |
| ThreeTerminalResistor          | Three Terminal Resistor           | PHYSICAL | Res3, PhyRes3, ResPhy3, PhyResistor3  | p, n, b      |
| IdealCapacitor                 | Ideal Capacitor                   | IDEAL    | C, Cap, Capacitor, IdealC, IdealCap   | p, n         |
| PhysicalCapacitor              | Physical Capacitor                | PHYSICAL | PhyC, PhyCap, CapPhy, PhyCapacitor    | p, n         |
| ThreeTerminalCapacitor         | Three Terminal Capacitor          | PHYSICAL | Cap3, PhyCap3, CapPhy3, PhyCapacitor3 | p, n, b      |
| IdealInductor                  | Ideal Inductor                    | IDEAL    | L, Ind, Inductor, IdealL, IdealInd    | p, n         |
| PhysicalInductor               | Physical Inductor                 | PHYSICAL | PhyL, PhyInd, IndPhy, PhyInductor     | p, n         |
| ThreeTerminalInductor          | Three Terminal Inductor           | PHYSICAL | Ind3, PhyInd3, IndPhy3, PhyInductor3  | p, n, b      |
| PhysicalShort                  | Short-Circuit/ Net-Tie            | PHYSICAL | Short                                 | p, n         |
| DcVoltageSource                | DC Voltage Source                 | IDEAL    | V, Vdc, Vsrc                          | p, n         |
| PulseVoltageSource             | Pulse Voltage Source              | IDEAL    | Vpu, Vpulse                           | p, n         |
| CurrentSource                  | Ideal DC Current Source           | IDEAL    | I, Idc, Isrc                          | p, n         |
| VoltageControlledVoltageSource | Voltage Controlled Voltage Source | IDEAL    | Vcvs, VCVS                            | p, n, cp, cn |
| CurrentControlledVoltageSource | Current Controlled Voltage Source | IDEAL    | Ccvs, CCVS                            | p, n, cp, cn |
| VoltageControlledCurrentSource | Voltage Controlled Current Source | IDEAL    | Vccs, VCCS                            | p, n, cp, cn |
| CurrentControlledCurrentSource | Current Controlled Current Source | IDEAL    | Cccs, CCCS                            | p, n, cp, cn |
| Bipolar                        | Bipolar Transistor                | PHYSICAL | Bjt, BJT                              | c, b, e      |
| Diode                          | Diode                             | PHYSICAL | D                                     | p, n         |

Each primitive is available in the `hdl21.primitives` namespace, either through its full name or any of its aliases. Most primitives have fairly verbose names (e.g. `VoltageControlledCurrentSource`, `IdealResistor`), but also expose short-form aliases (e.g. `Vcvs`, `R`). Each of the aliases in Table 1 above refer to _the same_ Python object, i.e.

```python
from hdl21.primitives import R, Res, IdealResistor

R is Res            # evaluates to True
R is IdealResistor  # also evaluates to True
```

Hdl21 `Primitives` come in _ideal_ and _physical_ flavors. The difference is most frequently relevant for passive elements, which can for example represent either

- (a) technology-specific passives, e.g. a MIM or MOS capacitor, or
- (b) an _ideal_ capacitor

Some element-types have solely physical implementations, some are solely ideal, and others include both.

### `ExternalModules`

Alternately Hdl21 includes an `ExternalModule` type which defines the interface to a module-implementation outside Hdl21. These external definitions are common for instantiating technology-specific modules and libraries. Think of them as a module "function header"; other popular modern HDLs refer to them as module _black boxes_.

An example `ExternalModule`:

```python
import hdl21 as h
from hdl21.prefix import µ
from hdl21.primitives import Diode

@h.paramclass
class BandGapParams:
    self_destruct = h.Param(
        dtype=bool,
        desc="Whether to include the self-destruction feature",
        default=True,
    )

BandGap = h.ExternalModule(
    name="BandGap",
    desc="Example ExternalModule, defined outside Hdl21",
    port_list=[h.Port(name="vref"), h.Port(name="enable")],
    paramtype=BandGapParams,
)
```

Both `Primitives` and `ExternalModules` have names, ordered `Ports`, and a few other pieces of metadata, but no internal implementation: no internal signals, and no instances of other modules. Unlike `Modules`, both _do_ have parameters. `Primitives` each have an associated `paramclass`, while `ExternalModules` can optionally declare one via their `paramtype` attribute. Their parameter-types are limited to a small subset of those possible for `Generators` - generally "scalar" types such as numbers, strings, and `Scalar` - primarily limited by the need to need to provide them to legacy HDLs. Parameters are applied in the same style as for `Generators`, by calling the `Primitive` or `ExternalModule`. Parameter-applications can either be an instance of the module's `paramtype` or a set of keyword arguments which validly contruct one inline.

```python
# Continuing from the snippet above:
params = BandGapParams(self_destruct=False)  # Watch out there!
```

`Primitives` and `ExternalModules` can be instantiated and connected in all the same styles as `Modules`:

```python
@h.module
class BandGapPlus:
    vref, enable = h.Signals(2)
    # Instantiate the `ExternalModule` defined above
    bg = BandGap(params)(vref=vref, enable=enable)
    # ...Anything else...

@h.module
class DiodePlus:
    p, n = h.Signals(2)
    # Parameterize, instantiate, and connect a `primitives.Diode`
    d = Diode(w=1 * µ, l=1 * µ)(p=p, n=n)
    # ... Everything else ...
```

## Exporting and Importing

Hdl21 generates hardware databases in the [VLSIR](https://github.com/Vlsir/Vlsir) interchange formats, defined through [Google Protocol Buffers](https://developers.google.com/protocol-buffers/). Through [VLSIR's Python tools](https://pypi.org/project/vlsirtools/) Hdl21 also includes drivers for popular industry-standard data formats and popular spice-class simulation engines.

The `hdl21.to_proto()` function converts an Hdl21 `Module` or group of `Modules` into a VLSIR `Package`. The `hdl21.from_proto()` function similarly imports a VLSIR `Package` into a Python namespace of Hdl21 `Modules`.

Exporting to industry-standard netlist formats is a particularly common operation for Hdl21 users. The `hdl21.netlist()` function uses VLSIR to export any of its supported netlist formats.

```python
import sys
import hdl21 as h

@h.module
class Rlc:
    p, n = h.Ports(2)

    res = h.Res(r=1e3)(p=p, n=n)
    cap = h.Cap(c=1e3)(p=p, n=n)
    ind = h.Ind(l=1e-9)(p=p, n=n)

# Write a spice-format netlist to stdout
h.netlist(Rlc, sys.stdout, fmt="spice")
```

`hdl21.netlist` takes a second destination argument `dest`, which is commonly either an open file-handle or `sys.stdout`.

Each `Module` includes a list of `Literal` contents, designed to be included directly in exported netlists. These are commonly used to refer to out-of-Hdl21 quantities, or to include netlist-language features not first-class supported by Hdl21. Example:

```python
@h.module
class HasLiterals:
    a, b, c = h.Ports(3)

# Add some literal content
HasLiterals.literals.extend([
    h.Literal("generate some_verilog_code"),
    h.Literal(".some_spice_attribute what=ever"),
    h.Literal("PRAGMA: some_pragma"),
])
```

`Module.literals` is a Python built-in list and can be manipulated with any of its typical methods (`append`, `extend`, etc.). Literals are written to netlists in the order they appear in the list. Order between Literals and other Module content is not preserved.

## Spice-Class Simulation

Hdl21 includes drivers for popular spice-class simulation engines commonly used to evaluate analog circuits.
The `hdl21.sim` package includes a wide variety of spice-class simulation constructs, including:

- DC, AC, Transient, Operating-Point, Noise, Monte-Carlo, Parameter-Sweep and Custom (per netlist language) Analyses
- Control elements for saving signals (`Save`), simulation options (`Options`), including external files and contents (`Include`, `Lib`), measurements (`Meas`), simulation parameters (`Param`), and literal netlist commands (`Literal`)

The entrypoint to Hdl21-driven simulation is the simulation-input type `hdl21.sim.Sim`. Each `Sim` includes:

- A testbench Module `tb`, and
- A list of simulation attributes (`attrs`), including any and all of the analyses, controls, and related elements listed above.

Example:

```python
import hdl21 as h
from hdl21.sim import *

@h.module
class MyModulesTestbench:
    # ... Testbench content ...

# Create simulation input
s = Sim(
    tb=MyModulesTestbench,
    attrs=[
        Param(name="x", val=5),
        Dc(var="x", sweep=PointSweep([1]), name="mydc"),
        Ac(sweep=LogSweep(1e1, 1e10, 10), name="myac"),
        Tran(tstop=11 * h.prefix.p, name="mytran"),
        SweepAnalysis(
            inner=[Tran(tstop=1, name="swptran")],
            var="x",
            sweep=LinearSweep(0, 1, 2),
            name="mysweep",
        ),
        MonteCarlo(
            inner=[Dc(var="y", sweep=PointSweep([1]), name="swpdc")],
            npts=11,
            name="mymc",
        ),
        Save(SaveMode.ALL),
        Meas(analysis="mytr", name="a_delay", expr="trig_targ_something"),
        Include("/home/models"),
        Lib(path="/home/models", section="fast"),
        Options(reltol=1e-9),
    ],
)

# And run it!
sim.run()
```

`Sim` also includes a class-based syntax similar to `Module` and `Bundle`. This also allows for inline definition of a testbench module, which can be named either `tb` or `Tb`:

```python
import hdl21 as h
from hdl21.sim import *

@sim
class MySim:

    @h.module
    class Tb:
        # ... Testbench content ...

    x = Param(5)
    y = Param(6)
    mydc = Dc(var=x, sweep=PointSweep([1]))
    myac = Ac(sweep=LogSweep(1e1, 1e10, 10))
    mytran = Tran(tstop=11 * h.prefix.PICO)
    mysweep = SweepAnalysis(
        inner=[mytran],
        var=x,
        sweep=LinearSweep(0, 1, 2),
    )
    mymc = MonteCarlo(inner=[Dc(var="y", sweep=PointSweep([1]), name="swpdc")], npts=11)
    delay = Meas(analysis=mytran, expr="trig_targ_something")
    opts = Options(reltol=1e-9)

    save_all = Save(SaveMode.ALL)
    a_path = "/home/models"
    include_that_path = Include(a_path)
    fast_lib = Lib(path=a_path, section="fast")

MySim.run()
```

Note that in these class-based definitions, attributes whose names don't really matter such as `save_all` above can be _named_ anything, but must be _assigned_ into the class, not just constructed.

Class-based `Sim` definitions retain all class members which are `SimAttr`s and drop all others. Non-`SimAttr`-valued fields can nonetheless be handy for defining intermediate values upon which the ultimate SimAttrs depend, such as the `a_path` field in the example above.

Classes decorated by `@sim` have a single special required field: a testbench attribute, named either `tb` or `Tb`, which sets the simulation testbench. A handful of names are disallowed in `sim` class-definitions, generally corresponding to the names of the `Sim` class's fields and methods such as `attrs` and `run`.

Each `sim` also includes a set of methods to add simulation attributes from their keyword constructor arguments. These methods use the same names as the simulation attributes (`Dc`, `Meas`, etc.) but incorporating the python language convention that functions and methods be lowercase (`dc`, `meas`, etc.). Example:

```python
# Create a `Sim`
s = Sim(tb=MyTb)

# Add all the same attributes as above
p = s.param(name="x", val=5)
dc = s.dc(var=p, sweep=PointSweep([1]), name="mydc")
ac = s.ac(sweep=LogSweep(1e1, 1e10, 10), name="myac")
tr = s.tran(tstop=11 * h.prefix.p, name="mytran")
noise = s.noise(
    output=MyTb.p,
    input_source=MyTb.v,
    sweep=LogSweep(1e1, 1e10, 10),
    name="mynoise",
)
sw = s.sweepanalysis(inner=[tr], var=p, sweep=LinearSweep(0, 1, 2), name="mysweep")
mc = s.montecarlo(
    inner=[Dc(var="y", sweep=PointSweep([1]), name="swpdc"),], npts=11, name="mymc",
)
s.save(SaveMode.ALL)
s.meas(analysis=tr, name="a_delay", expr="trig_targ_something")
s.include("/home/models")
s.lib(path="/home/models", section="fast")
s.options(reltol=1e-9)

# And run it!
s.run()
```

## Process Technologies

Designing for a specific implementation technology (or "process development kit", or PDK) with Hdl21 can use either of (or a combination of) two routes:

- Instantiate `ExternalModules` corresponding to the target technology. These would commonly include its process-specific transistor and passive modules, and potentially larger cells, for example from a cell library. Such external modules are frequently defined as part of a PDK (python) package, but can also be defined anywhere else, including inline among Hdl21 generator code.
- Use `hdl21.Primitives`, each of which is designed to be a technology-independent representation of a primitive component. Moving to a particular technology then generally requires passing the design through an `hdl21.pdk`'s `compile` function.

Hdl21 PDKs are Python packages which generally include two primary elements:

- (a) A library `ExternalModules` describing the technology's cells, and
- (b) A `compile` conversion-method which transforms a hierarchical Hdl21 tree, mapping generic `hdl21.Primitives` into the tech-specific `ExternalModules`.

Since PDKs are python packages, using them is as simple as importing them. Hdl21 includes a built-in sample PDK available via `hdl21.pdk.sample_pdk` which includes simulatable NMOS and PMOS transistors. Hdl21's source tree includes three additional PDK packages:

|                                       | PyPi                                   | Source        |
| ------------------------------------- | -------------------------------------- | ------------- |
| ASAP7 Predictive/ Academic PDK        | https://pypi.org/project/asap7-hdl21/  | [pdks/Asap7](./pdks/Asap7)  |
| SkyWater 130nm Open-Source PDK        | https://pypi.org/project/sky130-hdl21/ | [pdks/Sky130](./pdks/Sky130) |
| GlobalFoundries 180nm Open-Source PDK | https://pypi.org/project/gf180-hdl21   | [pdks/Gf180](./pdks/Gf180)  |

Each contain much more detail documentation on their specific installation and use.

```python
import hdl21 as h
import sky130_hdl21

@h.module
class SkyInv:
    """ An inverter, demonstrating using PDK modules """

    # Create some IO
    i, o, VDD, VSS = h.Ports(4)

    p = sky130_hdl21.Sky130MosParams(w=1,l=1)

    # And create some transistors!
    ps = sky130_hdl21.primtives.PMOS_1p8V_STD(p)(d=o, g=i, s=VDD, b=VDD)
    ns = sky130_hdl21.primtives.NMOS_1p8V_STD(p)(d=o, g=i, s=VSS, b=VSS)
```

Process-portable modules instead use Hdl21 `Primitives`, which can be compiled to a target technology:

```python
import hdl21 as h
from hdl21.prefix import µ
from hdl21.primitives import Nmos, Pmos, MosVth

@h.module
class Inv:
    """ An inverter, demonstrating instantiating PDK modules """

    # Create some IO
    i, o, VDD, VSS = h.Ports(4)

    # And now create some generic transistors!
    ps = Pmos(w=1*µ, l=1*µ, vth=MosVth.STD)(d=o, g=i, s=VDD, b=VDD)
    ns = Nmos(w=1*µ, l=1*µ, vth=MosVth.STD)(d=o, g=i, s=VSS, b=VSS)
```

Compiling the generic devices to a target PDK then just requires a pass through the PDK's `compile()` method:

```python
import hdl21 as h
import sky130_hdl21

sky130_hdl21.compile(Inv) # Produces the same content as `SkyInv` above
```

Hdl21 includes an `hdl21.pdk` subpackage which tracks the available in-memory PDKs. If there is a single PDK available, it need not be explicitly imported: `hdl21.pdk.compile()` will use it by default.

```python
import hdl21 as h
import sky130  # Note this import can be elsewhere in the program, i.e. in a configuration layer.

h.pdk.compile(Inv)  # With `sky130` in memory, this does the same thing as above.
```

### PDK Corners

The `hdl21.pdk` package inclues a three-valued `Corner` enumerated type and related classes for describing common process-corner variations. In pseudo [type-union](https://peps.python.org/pep-0604/) code:

```
Corner = TYP | SLOW | FAST
```

Typical technologies includes several quantities which undergo such variations. Values of the `Corner` enum can mean either the variations in a particular quantity, e.g. the "slow" versus "fast" variations of a poly resistor, or can just as oftern refer to a set of such variations within a given technology. In the latter case `Corner` values are often expanded by PDK-level code to include each constituent device variation. For example `my.pdk.corner(Corner.FAST)` may expand to definitions of "fast" Cmos transistors, resistors, and capacitors.

Quantities which can be varied are often keyed by a `CornerType`. In similar pseudo-code:

```
CornerType = MOS | CMOS | RES | CAP | ...
```

A particularly common such use case pairs NMOS and PMOS transistors into a `CmosCornerPair`. CMOS circuits are then commonly evauated at its four extremes, plus their typical case. These five conditions are enumerated in the `CmosCorner` type:

```python
@dataclass
class CmosCornerPair:
    nmos: Corner
    pmos: Corner
```

```
CmosCorner = TT | FF | SS | SF | FS
```

Hdl21 exposes each of these corner-types as Python enumerations and combinations thereof. Each PDK package then defines its mapping from these `Corner` types to the content they include, typically in the form of external files.

### PDK Installations and Sites

Much of the content of a typical process technology - even the subset that Hdl21 cares about - is not defined in Python. Transistor models and SPICE "library" files, such as those defining the `PMOS` and `NMOS` above, are common examples pertinent to Hdl21. Tech-files, layout libraries, and the like are similarly necessary for related pieces of EDA software. These PDK contents are commonly stored in a technology-specific arrangement of interdependent files. Hdl21 PDK packages structure this external content as a `PdkInstallation` type.

Each `PdkInstallation` is a runtime type-checked Python `dataclass` which extends the base `hdl21.pdk.PdkInstallation` type. Installations are free to define arbitrary fields and methods, which will be type-validated for each `Install` instance. Example:

```python
""" A sample PDK package with an `Install` type """

from pydantic.dataclasses import dataclass
from hdl21.pdk import PdkInstallation

@dataclass
class Install(PdkInstallation):
    """Sample Pdk Installation Data"""

    model_lib: Path  # Filesystem `Path` to transistor models
```

The name of each PDK's installation-type is by convention `Install` with a capital I. PDK packages which include an installation-type also conventionally include an `Install` instance named `install`, with a lower-case i. Code using the PDK package can then refer to the PDK's `install` attribute. Extending the example above:

```python
""" A sample PDK package with an `Install` type """

@dataclass
class Install(PdkInstallation):
    """Sample Pdk Installation Data"""

    model_lib: Path  # Filesystem `Path` to transistor models

install: Optional[Install] = None  # The active installation, if any
```

The content of this installation data varies from site to site. To enable "site-portable" code to use the PDK installation, Hdl21 PDK users conventionally define a "site-specific" module or package which:

- Imports the target PDK module
- Creates an instance of its `PdkInstallation` subtype
- Affixes that instance to the PDK package's `install` attribute

For example:

```python
# In "sitepdks.py" or similar
import mypdk

mypdk.install = mypdk.Install(
    models = "/path/to/models",
    path2 = "/path/2",
    # etc.
)
```

These "site packages" are named `sitepdks` by convention. They can often be shared among several PDKs on a given filesystem. Hdl21 includes one built-in example such site-package, [SampleSitePdks](./SampleSitePdks/), which demonstrates setting up both built-in PDKs, Sky130 and ASAP7:

```python
# The built-in sample `sitepdks` package
from pathlib import Path

import sky130_hdl21
sky130_hdl21.install = sky130_hdl21.Install(model_lib=Path("pdks") / "sky130" / ... / "sky130.lib.spice")

import asap7_hdl21
asap7_hdl21.install = asap7_hdl21.Install(model_lib=Path("pdks") / "asap7" / ... / "TT.pm")
```

"Site-portable" code requiring external PDK content can then refer to the PDK package's `install`, without being directly aware of its contents.
An example simulation using `mypdk`'s models with the `sitepdk`s defined above:

```python
# sim_my_pdk.py
import hdl21 as h
from hdl21.sim import Lib
import sitepdks as _ # <= This sets up `mypdk.install`
import mypdk

@h.sim
class SimMyPdk:
    # A set of simulation input using `mypdk`'s installation
    tb = MyTestBench()
    models = Lib(
        path=mypdk.install.models, # <- Here
        section="ss"
    )

# And run it!
SimMyPdk.run()
```

Note that `sim_my_pdk.py` need not necessarily import or directly depend upon `sitepdks` itself. So long as `sitepdks` is imported and configures the PDK installation anywhere in the Python program, further code will be able to refer to the PDK's `install` fields.

### Creating PDK Packages

Hdl21's source tree includes a [cookiecutter template](https://github.com/cookiecutter/cookiecutter) for creating a new PDK package, available at [pdks/PdkTemplate](./pdks/PdkTemplate).

## Bundles

Hdl21 `Bundle`s are _structured connection types_ which can include `Signal`s and instances of other `Bundle`s.
Think of them as "connection structs". Similar ideas are implemented by Chisel's `Bundle`s and SystemVerilog's `interface`s.

```python
@h.bundle
class Diff:
    p = h.Signal()
    n = h.Signal()

@h.bundle
class Quadrature:
    i = Diff()
    q = Diff()
```

Like `Module`s, `Bundle`s can be defined either procedurally or as a class decorated by the `hdl21.bundle` function.

```python
# This creates the same stuff as the class-based definitions above:

Diff = h.Bundle(name="Diff")
Diff.add(h.Signal(name="p"))
Diff.add(h.Signal(name="n"))

Quadrature = h.Bundle(name="Quadrature")
Quadrature.add(Diff(name="i"))
Quadrature.add(Diff(name="q"))
```

Calling a `Bundle` as in the calls to `Diff()` and `Diff(name=q)` creates an instance of that `Bundle`.

## Bundle Ports

Bundles are commonly most valuable for shipping collections of related `Signal`s between `Module`s.
Modules can accordingly have Bundle-valued ports. To create a Bundle-port, set the `port` argument to either the boolean `True`
or the `hdl21.Visibility.PORT` value.

```python
@h.module
class HasDiffs:
    d1 = Diff(port=True)
    d2 = Diff(port=h.Visbility.PORT)
```

Port directions on bundle-ports can be set by either of two methods.
The first is to set the directions directly on the Bundle's constituent `Signal`s.
To swap directions, pass the bundle-instances through the `hdl21.flipped` function,
or set the `flipped` argument to the instance-constructor.

```python
@h.bundle
class Inner:
    i = h.Input()
    o = h.Output()

@h.bundle
class Outer:
    b1 = Inner()
    b2 = h.flipped(Inner())
    b3 = Inner(flipped=True)
```

Here:

- An `Inner` bundle defines an `Input` and an `Output`
- An `Outer` bundle instantiates three of them
  - Instance `b1` is not flipped; its `i` is an input, and its `o` is an output
  - Instance `b2` is flipped; its `i` is an _output_, and its `o` is an _input_
  - Instance `b3` is also flipped, via its constructor argument

These "flipping based" bundles require that all constituent signals, including nested ones, have port-visibility.
The rules for flipping port directions are:

- Inputs become Outputs
- Outputs become Inputs
- Inouts and undirected ports (`direction=NONE`) retain their directions

```python
@h.bundle
class B:
    clk = h.Output()
    data = h.Input()

@h.module
class X: # Module with a `clk` output and `data` input
    b = B(port=True)

@h.module
class Y: # Module with a `clk` input and `data` output
    b = B(flipped=True, port=True)

@h.module
class Z:
    b = B() # Internal instance of the `B` bundle
    x = X(b=b)
    y = Y(b=b)
```

The second method for setting bundle-port directions is with `Role`s.
Each Hdl21 bundle either explicitly or implictly defines a set of `Role`s, which might alternately be called "endpoints".
These are the expected "end users" of the Bundle.
Signal directions are then defined on each signal's `src` (source) and `dest` (destination) arguments, which can be set to any of the bundle's roles.

```python
@h.roles
class HostDevice(Enum):
    HOST = auto()
    DEVICE = auto()

@h.bundle
class Jtag:
    roles = HostDevice # Set the bundle's roles
    # Note each signal sets one of the roles as `src` and another as `dest`
    tck, tdi, tms = h.Signals(3, src=roles.HOST, dest=roles.DEVICE)
    tdo = h.Signal(src=roles.DEVICE, dest=roles.HOST)
```

Bundle-valued ports are then assigned a role and associated signal-port directions via their `role` constructor argument.

```python
@h.module
class Widget: # with a Jtag Device port
    jtag = Jtag(port=True, role=Jtag.roles.DEVICE)

@h.module
class Debugger: # with a Jtag Host port
    jtag = Jtag(port=True, role=Jtag.roles.HOST)

@h.module
class System: # combining the two
    widget = Widget()
    debugger = Debugger(jtag=widget.jtag)
```

The rules for port-directions of role-based bundles are:

- If the bundle's role is the signal's source, the signal is an `Output`
- If the bundle's role is the signal's destination, the signal is an `Input`
- Otherwise the signal is assigned no direction, i.e. `direction=NONE`

## Collecting Bundles

It is often helpful or necessary to collect existing signals into a bundle, or to "re-arrange" signals from one bundle into another.
The primary mechanism for doing so is the `hdl21.bundlize` function which creates them.
Each call to `bundlize` creates an "anonymous" bundle which lacks a backing bundle-definition type.

```python
@h.bundle
class Uart:
    tx = h.Output()
    rx = h.Input()

@h.module
class HasUart:
    # Module with a `Uart` port
    uart = Uart(port=True)

@h.module
class ConnectTwo:
    # Connect two `HasUart`s, swapping `tx` and `rx`.
    uart = Uart()
    m1 = HasUart(uart=uart)
    m2 = HasUart(uart=h.bundlize(tx=uart.rx, rx=uart.tx))
```

## Examples

### Built-In Examples Library

Hdl21's source tree includes a built-in [examples](./examples/) library. Each is designed to be a straightforward but realistic use-case, and is a self-contained Python program which can be run directly, e.g. with:

```bash
python examples/rdac.py
```

The built-in examples include:

- [Current DAC](./examples/idac.py)
- [MOS Transistor Simulation](./examples/mos_sim.py)
- [Ring Oscillator Generator](./examples/ro.py)
- [Resistor-Ladder DAC](./examples/rdac.py)
- [Recursive Binary to One-Hot Encoders](./examples/encoder.py)

Reading, copying, or cloning these example programs is generally among the best ways to get started.  
And adding an example is a **highly** encouraged form of [pull request](https://github.com/dan-fritchman/Hdl21/pulls)!

### Featured Community Examples

- [Continuous-Time Delta-Sigma ADC Generators](https://github.com/aviralpandey/CT-DS-ADC_generator)
- [USB 2.0 PHY](https://github.com/Vlsir/Usb2Phy/tree/main/Usb2PhyAna)
- [VCO-Based ADC Generators](https://github.com/aviralpandey) (Coming soon!)

## Related Projects

- [VLSIR](https://github.com/vlsir/vlsir)
- [Hdl21 Schematics](https://github.com/vlsir/hdl21schematics)
- [Layout21](https://github.com/dan-fritchman/Layout21)

## Why Use Python?

Custom IC design is a complicated field. Its practitioners have to know
[a](https://people.eecs.berkeley.edu/~boser/courses/240B/lectures/M07%20OTA%20II.pdf) |
[lot](http://rfic.eecs.berkeley.edu/~niknejad/ee142_fa05lects/pdf/lect24.pdf) |
[of](https://www.delroy.com/PLL_dir/ISSCC2004/PLLTutorialISSCC2004.pdf) |
[stuff](https://inst.eecs.berkeley.edu/~ee247/fa10/files07/lectures/L25_2_f10.pdf),
independent of any programming background. Many have little or no programming experience at all. Python is reknowned for its accessibility to new programmers, largely attributable to its concise syntax, prototyping-friendly execution model, and thriving community. Moreover, Python has also become a hotbed for many of the tasks hardware designers otherwise learn programming for: numerical analysis, data visualization, machine learning, and the like.

Hdl21 exposes the ideas they're used to - `Modules`, `Ports`, `Signals` - via as simple of a Python interface as it can. `Generators` are just functions. For many, this fact alone is enough to create powerfully reusable hardware.

## Why _Not_ Use {X}?

We know you have plenty of choice when you fly, and appreciate you choosing Hdl21.  
A few alternatives and how they compare:

### Schematics

Graphical schematics have been the lingua franca of the custom-circuit field for, well, as long as it's been around. Most practitioners are most comfortable in this graphical form. (For plenty of circuits, so are Hdl21's authors.) Their most obvious limitation is the lack of capacity for programmable manipulation via something like Hdl21 `Generators`. Some schematic-GUI programs attempt to include "embedded scripting", perhaps even in Hdl21's own language (Python). We see those GUIs as entombing your programs in their badness. Hdl21 is instead a library, designed to be used by any Python program you like, sharable and runnable by anyone who has Python. (Which is everyone.)

### Netlists (Spice et al)

Take all of the shortcomings listed for schematics above, and add to them an under-expressive, under-specified, ill-formed, incomplete suite of "programming languages", and you've got netlists. Their primary redeeming quality: existing EDA CAD tools take them as direct input. So Hdl21 Modules export netlists of most popular formats instead.

### (System)Verilog, VHDL, other Existing Dedicated HDLs

The industry's primary, 80s-born digital HDLs Verilog and VHDL have more of the good stuff we want here - notably an open, text-based format, and a more reasonable level of parametrization. And they have the desirable trait of being primary input to the EDA industry's core tools. They nonetheless lack the levels of programmability present here. And they generally require one of those EDA tools to execute and do, well, much of anything. Parsing and manipulating them is well-reknowned for requiring a high pain tolerance. Again Hdl21 sees these as export formats.

### Chisel

Explicitly designed for digital-circuit generators at the same home as Hdl21 (UC Berkeley), Chisel encodes RTL-level hardware in Scala-language classes. It's the closest of the alternatives in spirit to Hdl21. (And it's aways more mature.) If you want big, custom, RTL-level circuits - processors, full SoCs, and the like - you should probably turn to Chisel instead. Chisel makes a number of decisions that make it less desirable for custom circuits, and have accordingly kept their designers' hands-off.

The Chisel library's primary goal is producing a compiler-style intermediate representation (FIRRTL) to be manipulated by a series of compiler-style passes. We like the compiler-style IR (and may some day output FIRRTL). But custom circuits really don't want that compiler. The point of designing custom circuits is dictating exactly what comes out - the compiler _output_. The compiler is, at best, in the way.

Next, Chisel targets _RTL-level_ hardware. This includes lots of things that would need something like a logic-synthesis tool to resolve to the structural circuits targeted by Hdl21. For example in Chisel (as well as Verilog and VHDL), it's semantically valid to perform an operation like `Signal + Signal`. In custom-circuit-land, it's much harder to say what that addition-operator would mean. Should it infer a digital adder? Short two currents together? Stick two capacitors in series?
Many custom-circuit primitives such as individual transistors actively fight the signal-flow/RTL modeling style assumed by the Chisel semantics and compiler. Again, it's in the way. Perhaps more important, many of Chisel's abstractions actively hide much of the detail custom circuits are designed to explicitly create. Implicit clock and reset signals serve as prominent examples.

Above all - Chisel is embedded in Scala. It's niche, it's complicated, it's subtle, it requires dragging around a JVM. It's not a language anyone would recommend to expert-designer/ novice-programmers for any reason other than using Chisel. For Hdl21's goals, Scala itself is Chisel's biggest burden.

### Other Fancy Modern HDLs

There are lots of other very cool hardware-description projects out there which take Hdl21's big-picture approach - embedding hardware idioms as a library in a modern programming languare. All focus on logical and/or RTL-level descriptions, unlike Hdl21's structural/ custom/ analog focus. We recommend checking them out:

- [SpinalHDL](https://github.com/SpinalHDL/SpinalHDL)
- [MyHDL](http://www.myhdl.org/)
- [Migen](https://github.com/m-labs/migen) / [nMigen](https://github.com/m-labs/nmigen)
- [Magma](https://github.com/phanrahan/magma)
- [PyMtl](https://github.com/cornell-brg/pymtl) / [PyMtl3](https://github.com/pymtl/pymtl3)
- [Clash](https://clash-lang.org/)

---

## Development

- Clone this repository & navigate to it.
- `bash scripts/install-dev.sh`. See the note below.
- `pytest -s` should yield something like:

```
$ pytest -s
============================ test session starts =============================
platform darwin -- Python 3.10.0, pytest-7.1.2, pluggy-1.0.0
plugins: anyio-3.5.0, cov-3.0.0
collected 126 items

hdl21/pdk/test_pdk.py ...
hdl21/pdk/sample_pdk/test_sample_pdk.py ...
hdl21/sim/tests/test_sim.py .........s
hdl21/tests/test_builtin_generators.py ..
hdl21/tests/test_bundles.py ............
hdl21/tests/test_conns.py ..............
hdl21/tests/test_exports.py x............
hdl21/tests/test_hdl21.py ...............x..............x...x........x...
hdl21/tests/test_params.py .....x
hdl21/tests/test_prefix.py ..........
hdl21/tests/test_source_info.py .
pdks/Asap7/asap7/test_asap7.py .
pdks/Sky130/sky130/test_sky130.py ....

================= 119 passed, 1 skipped, 6 xfailed in 0.55s ==================
```

Note: Hdl21 is commonly co-developed with the [VLSIR](https://github.com/Vlsir/Vlsir) interchange formats.
The [scripts](./scripts) folder includes two short installation scripts which install VLSIR from either PyPi or GitHub. Tweaks to PyPi-released versions Hdl21 may be able to use the PyPi versions of VLSIR. Most Hdl21 development cannot, and should clone VLSIR from GitHub. The `install-dev` script will install VLSIR alongside `Hdl21/`, i.e. in the parent directory of the Hdl21 clone.
