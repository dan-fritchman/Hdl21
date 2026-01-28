
# IHP SG13G2 Hdl21

Hdl21 PDK package for the open-source IHP SG13G2 130nm BiCMOS PDK.


## About This Technology

IHP SG13G2 is a 130nm BiCMOS technology featuring high-performance SiGe:C npn-HBTs with:
- fT up to 350 GHz
- fmax up to 450 GHz

This makes it particularly well-suited for RF, high-speed analog, and mixed-signal applications.

The IHP Open PDK is developed and maintained by IHP (Leibniz Institute for High Performance Microelectronics) as part of the open-source silicon ecosystem.

Related Projects:
- [IHP-Open-PDK](https://github.com/IHP-GmbH/IHP-Open-PDK) - Official IHP Open PDK repository
- [IHP GDSFactory PDK](https://github.com/IHP-GmbH/IHP-PDK) - Python/GDSFactory integration


## About this PDK Package

`ihp_hdl21` defines a set of `hdl21.ExternalModule`s comprising the essential devices of the IHP SG13G2 130nm BiCMOS PDK, and a `compile` method for converting process-portable `hdl21.Primitive` elements into these modules.


## Installation

Install from local source:

```
pip install -e pdks/IHP
```

And then import the package as `ihp_hdl21`:

```python
import ihp_hdl21
assert ihp_hdl21.primitives is not None  # etc
```


## PDK `Install` Data

Silicon process technologies generally require non-Python data to execute simulations and other tasks. IHP is no different. *Those files are not distributed as part of this package.* The `ihp_hdl21` package defines an Hdl21 `PdkInstallation` type `ihp_hdl21.Install`, which includes references to any such out-of-Python data, generally in the form of filesystem paths.

A typical installation setup:

```python
from pathlib import Path
import ihp_hdl21

# Point to your IHP-Open-PDK installation
pdk_path = Path("/path/to/IHP-Open-PDK/ihp-sg13g2")
model_lib = Path("libs.tech/ngspice/models")

ihp_hdl21.install = ihp_hdl21.Install(
    pdk_path=pdk_path,
    model_lib=model_lib
)
```

The IHP Open PDK supports simulation with:
- [ngspice](https://ngspice.sourceforge.io/)
- [Xyce](https://xyce.sandia.gov/)


## List of Available Devices

All PDK units are in microns (um).

1. [MOSFETs](#mosfets)
2. [HBT Bipolar Transistors](#hbt-bipolar-transistors)
3. [Resistors](#resistors)
4. [Capacitors](#capacitors)
5. [Diodes and ESD Devices](#diodes-and-esd-devices)


### MOSFETs

MOSFETs can be defined using width (W), length (L), and number of gate fingers (ng). The IHP PDK provides both low-voltage (1.2V core) and high-voltage (3.3V I/O) devices.

MOSFETs in Hdl21 are designed to be PDK-agnostic:

```python
import ihp_hdl21
from hdl21.primitives import Mos, MosType, MosFamily, MosVth

# Low-voltage NMOS
lv_nmos = Mos(vth=MosVth.STD, tp=MosType.NMOS, family=MosFamily.CORE)
ihp_hdl21.compile(lv_nmos)  # Compiles to sg13_lv_nmos

# High-voltage PMOS
hv_pmos = Mos(vth=MosVth.STD, tp=MosType.PMOS, family=MosFamily.IO)
ihp_hdl21.compile(hv_pmos)  # Compiles to sg13_hv_pmos
```

Or reference directly:

```python
from ihp_hdl21 import IhpMosParams
import ihp_hdl21.primitives as s

lv_nmos = s.LV_NMOS(IhpMosParams(w=1.0, l=0.13, ng=1))
```

| Component Key | MosType | MosFamily | SPICE Subcircuit | Min L (um) | Description |
|--------------|---------|-----------|------------------|------------|-------------|
| LV_NMOS | NMOS | CORE | sg13_lv_nmos | 0.13 | Low-voltage 1.2V NMOS |
| LV_PMOS | PMOS | CORE | sg13_lv_pmos | 0.13 | Low-voltage 1.2V PMOS |
| HV_NMOS | NMOS | IO | sg13_hv_nmos | 0.45 | High-voltage 3.3V NMOS |
| HV_PMOS | PMOS | IO | sg13_hv_pmos | 0.45 | High-voltage 3.3V PMOS |


### HBT Bipolar Transistors

IHP's SiGe:C HBTs are the highlight of this technology, offering exceptional RF performance.

**Important:** HBTs have 4 terminals (c, b, e, bn) where `bn` is the base node/substrate connection. This differs from the standard 3-terminal Hdl21 Bipolar primitive. For full control, use direct instantiation:

```python
from ihp_hdl21 import IhpHbtParams
import ihp_hdl21.primitives as s

hbt = s.NPN13G2(IhpHbtParams(Nx=1, Ny=1, m=1))
```

| Component Key | SPICE Subcircuit | Terminals | Description |
|--------------|------------------|-----------|-------------|
| NPN13G2 | npn13G2 | c, b, e, bn | Standard HBT |
| NPN13G2L | npn13G2l | c, b, e, bn | Large HBT |
| NPN13G2V | npn13G2v | c, b, e, bn | Variable emitter HBT |
| NPN13G2_5T | npn13G2_5t | c, b, e, bn, t | 5-terminal HBT |
| NPN13G2L_5T | npn13G2l_5t | c, b, e, bn, t | Large 5-terminal HBT |
| NPN13G2V_5T | npn13G2v_5t | c, b, e, bn, t | Variable 5-terminal HBT |
| PNPMPA | pnpMPA | c, b, e | Lateral PNP |


### Resistors

IHP resistors are 3-terminal devices with a bulk connection:

```python
from ihp_hdl21 import IhpResParams
import ihp_hdl21.primitives as s

# High-resistivity polysilicon resistor
rhigh = s.RHIGH(IhpResParams(w=0.5, l=10.0, m=1))
```

| Component Key | SPICE Subcircuit | Terminals | Sheet R | Description |
|--------------|------------------|-----------|---------|-------------|
| RSIL | rsil | p, n, b | ~7 ohm/sq | Silicided polysilicon |
| RHIGH | rhigh | p, n, b | ~1k ohm/sq | High-resistivity polysilicon |
| RPPD | rppd | p, n, b | ~300 ohm/sq | P-doped polysilicon |


### Capacitors

```python
from ihp_hdl21 import IhpCapParams
import ihp_hdl21.primitives as s

# MIM capacitor
cmim = s.CAP_CMIM(IhpCapParams(w=10.0, l=10.0, m=1))
```

| Component Key | SPICE Subcircuit | Terminals | Description |
|--------------|------------------|-----------|-------------|
| CAP_CMIM | cap_cmim | p, n | MIM capacitor |
| CAP_RFCMIM | cap_rfcmim | p, n, b | RF MIM capacitor |
| SVARICAP | sg13_hv_svaricap | g1, w, g2, bn | Varactor |


### Diodes and ESD Devices

```python
from ihp_hdl21 import IhpDiodeParams, IhpEsdParams
import ihp_hdl21.primitives as s

schottky = s.SCHOTTKY_NBL1(IhpDiodeParams())
esd = s.DIODEVDD_2KV(IhpEsdParams())
```

| Component Key | SPICE Subcircuit | Terminals | Description |
|--------------|------------------|-----------|-------------|
| SCHOTTKY_NBL1 | schottky_nbl1 | a, c, s | Schottky diode |
| DIODEVDD_2KV | diodevdd_2kv | vdd, pad, vss | ESD protection (2kV) |
| DIODEVDD_4KV | diodevdd_4kv | vdd, pad, vss | ESD protection (4kV) |
| DIODEVSS_2KV | diodevss_2kv | vdd, pad, vss | ESD protection (2kV) |
| DIODEVSS_4KV | diodevss_4kv | vdd, pad, vss | ESD protection (4kV) |


## Corner Models

The IHP PDK provides process corner models for simulation:

```python
import hdl21 as h
import ihp_hdl21

# Get typical corner model include for LV MOS
lib = ihp_hdl21.install.include_mos_lv(h.pdk.Corner.TYP)

# Available corners: TYP, FAST, SLOW
# Available include methods:
#   - include_mos_lv(corner)  - LV MOS
#   - include_mos_hv(corner)  - HV MOS
#   - include_hbt(corner)     - HBT
#   - include_res(corner)     - Resistors
#   - include_cap(corner)     - Capacitors
```


## Example: Simple Inverter

```python
import hdl21 as h
from hdl21.primitives import Mos, MosType, MosFamily
import ihp_hdl21

@h.module
class Inverter:
    vdd = h.Port()
    vss = h.Port()
    inp = h.Port()
    out = h.Port()

    # LV transistors (1.2V core)
    p = Mos(tp=MosType.PMOS, family=MosFamily.CORE)(
        g=inp, d=out, s=vdd, b=vdd
    )
    n = Mos(tp=MosType.NMOS, family=MosFamily.CORE)(
        g=inp, d=out, s=vss, b=vss
    )

# Compile to IHP technology
ihp_hdl21.compile(Inverter)

# Generate SPICE netlist
from io import StringIO
h.netlist(Inverter, StringIO(), fmt="spice")
```


## Development

```
pip install -e "pdks/IHP[dev]"
```

Run tests:
```
pytest pdks/IHP/ihp_hdl21/
```
