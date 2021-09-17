# HDL21

## Generator-Based Structural Hardware Description Library

[![test](https://github.com/dan-fritchman/Hdl21/actions/workflows/test.yaml/badge.svg)](https://github.com/dan-fritchman/Hdl21/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/dan-fritchman/Hdl21/branch/main/graph/badge.svg?token=f8LKUqEPdq)](https://codecov.io/gh/dan-fritchman/Hdl21)

Hdl21 is a library for efficiently creating and manipulating structural hardware descriptions such as those common in custom integrated circuits. Circuits are described in two primary units of re-use: 

- `Modules` are structural combinations of ports, signals, and instances of other `Modules`. 
- `Generator`s are Python functions that return `Modules`. 

In other words: 

- `Generators` are code. `Modules` are data. 
- `Generators` require a runtime environment. `Modules` do not. 

## Modules

Hdl21 `Modules` are type-specific containers of just a handful of `hdl21` types. They can include: 

* Instances of other `Modules`
* Connections between them defined by `Signals` and `Ports`
* Structured connections defined by `Interfaces` 

An example of creating a `Module`:

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

This class-based syntax produces identical results to the procedural code-block above. Its declarative style can be much more natural and expressive in many contexts, including for designers familiar with popular HDLs. 

Creation of `Module` signal-attributes is generally performed by the built-in `Signal`, `Port`, `Input`, and `Output` constructors. Each comes with a "plural version" (`Input*s*` etc.) which creates several identical objects at once:

```python
import hdl21 as h

@h.module
class MyModule:
    a, b = h.Inputs(2)
    c, d, e = h.Outputs(3, width=16)
    f, g, h, i = h.Signals(4)
```

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

Connections-by-assignment are performed by assigning either a `Signal` or another instance's `Port` to an attribute of a Module-Instance. 

```python 
# Create a module
m = h.Module()
# Create its internal Signals
m.a = Signal()
m.b = Signal()
m.c = Signal()
# Create an Instance
m.i1 = AnotherModule()
# And wire them up
m.i1.a = a
m.i1.b = b
m.i1.c = c
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

Hdl21 `Modules` are "plain old data". They require no runtime or execution environment. They can be (and are!) fully represented in markup languages such as JSON, YAML, or ProtoBuf. The power of embedding `Modules` in a general-purpose programming language lies in allowing code to create and manipulate them. Hdl21's `Generators` are functions which produce `Modules`, and have a number of built-in features to aid embedding in a hierarchical hardware tree. 

Creating a generator just requires applying the `@hdl21.generator` decorator to a function: 

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

Note in the latter example, the Module `Inner` is defined solely inside the generator-function body. It serves as a local, semi-private implementation space for the returned `Outer` module. The desire for these relatively hidden implementation-details are fairly common for hierarchical hardware designs. (Sorting out which Modules are designed to be used "publicly" is a common problem.) "Closure Modules" such as `Inner` are about as private such spaces as the Python language allows. 


## Parameters 

`Generators` typically take a single argument `params` which is a collection of `hdl21.Params`. Generator parameters are strongly type-checked at runtime. Each requires a data-type `dtype` and description-string `desc`. Optional parameters include a default-value, which must be an instance of `dtype`.

```python
npar = h.Param(dtype=int, desc="Number of parallel fingers", default=1)
```

The collections of these parameters used by `Generators` are called param-classes, and are typically formed by applying the `hdl21.paramclass` decorator to a class-body-full of `hdl21.Params`: 

```python
import hdl21 as h

@h.paramclass
class MyParams:
    # Required
    width = h.Param(dtype=int, desc="Input bit-width. Required")
    # Optional - including a default value
    text = h.Param(dtype=str, desc="An Optional string-valued parameter", default="My Favorite Module")
```

Each param-class is defined similarly to the Python standard-library's `dataclass`, but using assignment rather than type-annotation syntax. The `paramclass` decorator converts these class-definitions into type-checked `dataclasses`, with fields using the `dtype` of each parameter. 

```python
p = MyParams(width=8, text="Your Favorite Module")
assert p.width == 8  # Passes. Note this is an `int`, not a `Param`
assert p.text == "Your Favorite Module"  # Also passes 
```
 
The `paramclass` decorator also adds `descriptions` and `defaults` methods which provide dictionaries of each parameter's default-values and string-descriptions. Similar to `dataclasses`, param-class constructors use the field-order defined in the class body. Note Python's function-argument rules dictate that all required arguments be declared first, and all optional arguments come last. 

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

Param-classes are immutable and hashable, and therefore require their attributes to be as well. Two common types left out by these rules are `list` and `dict`. Lists are easily converted into tuples. Param-class creation performs these conversions inline: 

```python
@h.paramclass
class HasTuple:
    t = h.Param(dtype=tuple, desc="Go ahead, try a list")

h = HasTuple(t=[1, 2, 3])      # Give it a list
assert isinstance(h.t, tuple)  # Passes
assert h.t == (1, 2, 3)        # Also passes 
```

Dictionary-valued fields can instead be converted into more (potentially nested) param-classes. 

## A Note on Parametrization 

Hdl21 `Generators` have parameters. `Modules` do not. 

This is a deliberate decision, which in this sense makes `hdl21.Module` less feature-rich than the analogous `module` concepts in existing HDLs (Verilog, VHDL, and even SPICE). These languages support what might be called "static parameters" - relatively simple relationships between parent and child-module parameterization. Setting, for example, the width of a signal or number of instances in an array is straightforward. But more elaborate parametrization-cases are either highly cumbersome or altogether impossible to create. (As an example, try using Verilog parametrization to make a programmable-depth binary tree.) Hdl21, in contrast, exposes all parametrization to the full Python-power of its generators. 

## Primitives and External Modules

The leaf-nodes of each hierarchical Hdl21 circuit are generally defined in one of two places: 

* `Primitive` elements, typically defined by simulation tools and other EDA software. These include transistors, resistors, capacitors, and other irreducible components. Hdl21 defines a library of such elements in its `hdl21.primitives` module.
* Outside Hdl21, via `ExternalModules`

Hdl21 `Primitives` come in *ideal* and *physical* flavors. The difference is most frequently relevant for passive elements, which can represent either (a) technology-specific passives, e.g. a MIM or MOS capacitor, or (b) an *ideal*  capacitor. Some element-types have solely physical implementations, some are solely ideal, and others include both. A summary of the `hdl21.Primitives` and their flavors:

| Physical             | Ideal            | Alias(es)         | 
| ------------------   | ---------------- | ----------------- | 
| `PhysicalResistor`   | `IdealResistor`  | `R`, `Res`, `Resistor`  | 
| `PhysicalInductor`   | `IdealInductor`  | `L`, `Ind`, `Inductor`  | 
| `PhysicalCapacitor`  | `IdealCapacitor` | `C`, `Cap`, `Capacitor` | 
| `PhysicalShort`      | `IdealShort`     | `Short`                 | 
|                      | `VoltageSource`  | `Vsrc`, `V`             | 
|                      | `CurrentSource`  | `Isrc`, `I`             | 
| `Mos`                |                  |                         | 
| `Diode`              |                  | `D`                     | 

Alternately Hdl21 includes an `ExternalModule` type which defines the interface to a module-implementation outside Hdl21. These external definitions are common for instantiating technology-specific modules and libraries. (They might analogously be called *black boxes*.) An example `ExternalModule`: 

```python
import hdl21 as h 

@h.paramclass 
class BandGapParams:
    self_destruct = h.Param(
        dtype=bool, 
        desc="Whether to include the self-destruction feature", 
        default=True
    )

BandGap = h.ExternalModule(
    name="BandGap",
    desc="Example ExternalModule, defined outside Hdl21",
    port_list=[h.Port("vref"), h.Port("enable")],
    paramtype=BandGapParams
)
```

Both `Primitives` and `ExternalModules` have names, ordered `Ports`, and a few other pieces of metadata, but no internal implementation: no internal signals, and no instances of other modules. Unlike `Modules`, both *do* have parameters. `Primitives` each have an associated `paramclass`, while `ExternalModules` can optionally declare one via their `paramtype` attribute. Their parameter-types are typically limited to scalar numeric types (`int`, `float`) and `str` (a small subset of those possible for `Generators`) - primarily limited by the need to need to provide them to legacy HDLs. 

`Primitives` and `ExternalModules` can be instantiated and connectd in all the same styles as `Modules`: 

```python
import hdl21 as h

params = BandGapParams(self_destruct=False)  # Watch out there! 

@h.module
class BandGapPlus:
    vref, enable = h.Signals(2)
    bg = BandGap(params)          # Instantiate the `ExternalModule` defined above
    bg(vref=vref, enable=enable)  # And call to connect it
    # ... Everything else ...

params = h.primitives.DiodeParams(isat=1e-15)

@h.module
class DiodePlus:
    p, n = h.Signals(2)
    d = h.primitives.D(params)(p=p, n=n)  # Instantiate the Primitive Diode
    # ... Everything else ...
```

## Process Technologies

Designing for a specific implementation technology (or "process development kit", or PDK) with Hdl21 can use either of (or a combination of) two routes: 

* Instantiate `ExternalModules` corresponding to the target technology. These would commonly include its tech-specific transistor and passive modules, and potentially larger cells, for example from a cell library. 
* Use `hdl21.Primitives`, each of which is designed to be a technology-independent representation of a primitive component. Moving to a particular technology then generally requires passing the design through an `hdl21pdk` converter. 

Hdl21 PDKs are Python packages which generally include two primary elements: 

* (a) A library `ExternalModules` describing the technology's cells, and 
* (b) A `compile` conversion-method which transforms a hierarchical Hdl21 tree, mapping generic `hdl21.Primitives` into the tech-specific `ExternalModules`.


---
## Why Use Python?

Custom IC design is a complicated field. Its practitioners have to know a | lot | of | stuff, independent of any programming background. Many have little or no programming experience at all. Python is reknowned for its accessibility to new programmers, largely attributable to its concise syntax, prototyping-friendly execution model, and thriving community. Moreover, Python has also become a hotbed for many of the tasks hardware designers otherwise learn programming for: numerical analysis, data visualization, machine learning, and the like. 

Hdl21 exposes the ideas they're used to - `Modules`, `Ports`, `Signals` - via as simple of a Python interface as it can. `Generators` are just functions. For many, this fact alone is enough to create powerfully reusable hardware.

## Why *Not* Use {X}?

We know you have plenty of choice when you fly, and appreciate you choosing Hdl21. A few alternatives and how they compare: 

### Schematics

Graphical schematics have been the lingua franca of the custom-circuit field for, well, as long as it's been around. Most practitioners are most comfortable in this graphical form. (For plenty of circuits, so are Hdl21's authors.) Their most obvious limitation is the lack of capacity for programmable manipulation via something like Hdl21 `Generators`. Some schematic-GUI programs attempt to include "embedded scripting", perhaps even in Hdl21's own language (Python). We see those GUIs as entombing your programs in their badness. Hdl21 is instead a library, designed to be used by any Python program you like, sharable and runnable by anyone who has Python. (Which is everyone.) 

### Netlists (Spice et al)

Take all of the shortcomings listed for schematics above, and add to them an under-expressive, under-specified, ill-formed, incomplete suite of "programming languages", and you've got netlists. Their primary redeeming quality: existing EDA CAD tools take them as direct input. So Hdl21 Modules export netlists of most popular formats instead. 

### (System)Verilog, VHDL, other Existing Dedicated HDLs

The industry's primary, 80s-born digital HDLs Verilog and VHDL have more of the good stuff we want here - notably an open, text-based format, and a more reasonable level of parametrization. And they have the desirable trait of being primary input to the EDA industry's core tools. They nonetheless lack the levels of programmability present here. And they generally require one of those EDA tools to execute and do, well, much of anything. Parsing and manipulating them is well-reknowned for requiring a high pain tolerance. Again Hdl21 sees these as export formats. 

### Chisel

Explicitly designed for digital-circuit generators at the same home as Hdl21 (UC Berkeley), Chisel encodes RTL-level hardware in Scala-language classes. It's the closest of the alternatives in spirit to Hdl21. (And it's aways more mature.) If you want big, custom, RTL-level circuits - processors, full SoCs, and the like - you should probably turn to Chisel instead. Chisel makes a number of decisions that make it less desirable for custom circuits, and have accordingly kept their designers' hands-off. 

The Chisel library's primary goal is producing a compiler-style intermediate representation (FIRRTL) to be manipulated by a series of compiler-style passes. We like the compiler-style IR (and may some day output FIRRTL). But custom circuits really don't want that compiler. The point of designing custom circuits is dictating exactly what comes out - the compiler *output*. The compiler is, at best, in the way. 

Next, Chisel targets *RTL-level* hardware. This includes lots of things that would need something like a logic-synthesis tool to resolve to the structural circuits targeted by Hdl21. For example in Chisel (as well as Verilog and VHDL), it's semantically valid to perform an operation like `Signal + Signal`. In custom-circuit-land, it's much harder to say what that addition-operator would mean. Should it infer a digital adder? Short two currents together? Stick two capacitors in series? 
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

* Install [Poetry](https://python-poetry.org/docs/) (the cool-kids' TOML-configured `pip` replacement). Or drag `pip` along if you know how. 
* Clone this repo & navigate to it 
* `poetry install` will install all dependencies
* `pytest -s` should yield something like: 


```
$ pytest -s
=== test session starts ===
platform darwin -- Python 3.8.5, pytest-5.4.3, py-1.10.0, pluggy-0.13.1
rootdir: /home/Hdl21
collected 21 items                                                                    

hdl21/tests/test_hdl21.py .....................

=== 21 passed in 0.27s ===
```

