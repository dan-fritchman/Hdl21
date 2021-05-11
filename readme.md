# HDL21

## Generator-Based Structural Hardware Description Library

Hdl21 is a library for efficiently creating and manipulating structural hardware descriptions such as those common in custom integrated circuits. Circuits are described in two primary units of re-use: 

- `Modules` are structural combinations of ports, signals, instances of other `Modules`. 
- `Generator`s are Python functions that return `Modules`. 

In other words: 

- `Generators` are code. `Modules` are data. 
- `Generators` require a runtime environment. `Modules` do not. 
- `Generators` have parameters. `Modules` do not. 

## Modules

Modules have two definition syntaxes.
The procedural/ imperative one:

```python
import hdl21 as h 

m = h.Module(name="MyModule")
m.i = h.Input()
m.o = h.Output(width=8)
m.s = h.Signal()
m.a = h.Instance(AnotherModule)
```

`Modules` are type-specific containers of just a handful of `hdl21` types. They can include:

* `Instances` of other `Modules`
* IO defined by a set of `Ports`
* Internal `Signals`
* Hierarchical connections defined by (FIXME: `Bundles` or `Interfaces`, pick a name)


`Modules` can also be defined through a `class`-based syntax. Creating a sub-class of `hdl21.Module` produces a new `Module`-definition, in which each attribute can be declared like so: 

```python
import hdl21 as h 

class MyModule(h.Module):
    i = h.Input()
    o = h.Output(width=8)
    s = h.Signal()
    a = h.Instance(AnotherModule)
```

This class-based syntax produces identical results as the procedural code-block above. Its declarative style can be much more natural and expressive in many contexts, including for designers familiar with popular HDLs. 

## Connections 

Popular HDLs generally feature one of two forms of connection semantics. Verilog, VHDL, and most dedicated HDLs use "connect by call" semantics, in which signal-objects are first declared, then passed as function-call-style arguments to instances of other modules. 

```verilog
// Declare signals 
logic a, b, c;
// Verilog Instance
another_module i1 (a, b, c);
// Verilog Connect-by-Name Instance 
another_module i2 (.a(a), .b(b), .c(c));
```

Chisel, in contrast, uses "connection by assignment" - more literally using the walrus `:=` operator. Instances of child modules are created first, and their ports are directly walrus-connected to one another. No local-signal objects ever need be declared in the instantiating parent module. 

```scala
// Create Module Instances
val i1 = Module(new AnotherModule)
val i2 = Module(new AnotherModule)
// Wire them directly to one another 
i1.io.a := i2.io.a
i1.io.b := i2.io.b
i1.io.c := i2.io.c
```

Each can be more concise and expressive depending on context. Hdl21 `Modules` support both connect-by-call and connect-by-assignment forms. 

Connections-by-assignment are performed by assigning either a `Signal` or another instance's `Port` to an attribute of a Module-Instance. 

```python 
# Create a module
m = h.Module()
# Create its internal Signals
m.a = Signal()
m.b = Signal()
m.c = Signal()
# Create an Instance
m.i1 = h.Instance(AnotherModule)
# And wire it up
m.i1.a = a
m.i1.b = b
m.i1.c = c
```

This also works without the parent-module `Signals`:

```python
# Create a module
m = h.Module() 
# Create the Instances
m.i1 = h.Instance(AnotherModule)
m.i2 = h.Instance(AnotherModule)
# And wire it up
m.i1.a = m.i2.a
m.i1.b = m.i2.b
m.i1.c = m.i2.c
```

Instances can instead be connected by call:

```python
# Create a module
m = h.Module() 
# Create the Instances
m.i1 = h.Instance(AnotherModule)
m.i2 = h.Instance(AnotherModule)
# Call one to connect them
m.i1(a=m.i2.a, b=m.i2.b, c=m.i2.c)
```

These connection-calls can also be performed inline, as the instances are being created. 

```python
# Create a module
m = h.Module() 
# Create the Instance `i1`
m.i1 = h.Instance(AnotherModule)
# Create another Instance `i2`, and connect to `i1`
m.i2 = h.Instance(AnotherModule)(a=m.i1.a, b=m.i1.b, c=m.i1.c)
```

The `Module` class-syntax allows for quite a bit more magic in this respect. The `Module` class-body executes in dataflow/dependency order, allowing references to objects before they are declared. 

```python
class Thing(h.Module):
    inp = h.Input()
    out = h.Output()

class BackToBack(h.Module):
    t1 = h.Instance(Thing)(inp=t2.out, out=t2.inp) # Note there is no `t2` yet
    t2 = h.Instance(Thing)(inp=t1.out, out=t1.inp) # There it is
```

While this dependency-ordered execution applies to all `Module` contents, it's particularly handy for connections. 

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
    class MySecondGen(h.Module):
        i = h.Input(width=params.w)
    return MySecondGen
```

Or any combination of the two:

```python
@h.generator
def MyThirdGenerator(params: MyParams) -> h.Module:
    # Create an internal Module
    class Inner(h.Module):
        i = h.Input(width=params.w)

    # Manipulate it a bit
    Inner.o = h.Output(width=2 * Inner.i.width)

    # Instantiate that in another Module 
    class Outer(h.Module):
        inner = h.Instance(Inner)

    # And manipulate that some more too 
    Outer.inp = h.Input(width=params.w)
    return Outer
```

Note in the latter example, the Module `Inner` is defined solely inside the generator-function body. It serves as a local, semi-private implementation space for the returned `Outer` module. The desire for these relatively hidden implementation-details are fairly common for hierarchical hardware designs. (Sorting out which Modules are designed to be used "publicly" is a common problem.) "Closure Modules" such as `Inner` are about as private such spaces as the Python language allows. 


## Parameters 

`Generator` function-arguments allow for a few use-cases. The primary-such case is shown in each of the prior examples: `Generators` typically take a single argument `params`, which is a collection of `hdl21.Param` parameters. Parameters are strongly-typed and type-checked at runtime. Each requires a data-type `dtype` and description-string `desc`. Optional parameters include a default-value, which of course must be an instance of `dtype`.

```python
npar = h.Param(dtype=int, desc="Number of parallel fingers", default=1)
```

The collections of these parameters used by `Generators` are called param-classes, and are typically formed by applying the `hdl21.paramclass` decorator to a class-definition-full of `hdl21.Params`:  

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

Param-classes can be nested, and can be converted to (potentially nested) dictionaries via `dataclasses.asdict`. The same conversion applies in reverse - (potentially nested) dictionaries can be expanded and serve as param-class constructor arguments: 

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

h = HasTuple(t=[1, 2, 3])     # Give it a list
assert isinstance(h.t, tuple) # Passes
assert h.t == (1, 2, 3)       # Also passes 
```

Dictionary-valued fields can instead be converted into more (potentially nested) param-classes. 


## Why Use Python?

Custom IC design is a complicated field. Its practitioners have to know a | lot | of | stuff, independent of any programming background. Many have little or no programming experience at all. Python is reknowned for its accessibility to new programmers, largely attributable to its concise syntax, prototyping-friendly execution model, and thriving community. Moreover, Python has also become a hotbed for many of the tasks hardware designers otherwise learn programming for: numerical analysis, data visualization, machine learning, and the like. 

HDL21 exposes the ideas they're used to - `Modules`, `Ports`, `Signals` - via as simple of a Python interface as it can. `Generators` are just functions. For many, this fact alone is enough to create powerfully reusable hardware.

## Why *Not* Use {X}?

We understand you have plenty of choice in the HDL space, and appreciate you flying with HDL21.

### Graphical Schematics

Generator code plz

### Netlists (Spice et al)

These lack the generator stuff duh

### (System)Verilog, VHDL, or Existing Dedicated HDLs

They've got more better stuff.
Each born in the 80s, lack the dynamic generation capacity.

### Chisel

Explicitly designed for digital-circuit generators, at the same home as HDL21 (UC Berkeley), Chisel encodes RTL generators as Scala-language classes featuring an elaborate DSL.

- Dont want the FIRRTL compiler
- RTL-level target. E.g. `Signal + Signal`
- Abstractions hide much of the detail custom circuits are designed to explicitly create
- Many custom-circuit primitives such as individual transistors actively fight the dataflow RTL modeling style

Above all, towards HDL21's goals Scala itself is Chisel's largest burden.

### Other Fancy Modern HDLs

There are many of these, provide a list of links to them
All focus on generating RTL-level hardware

