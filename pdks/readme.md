# Hdl21 PDK Samples

Sample and example packages which serve as `hdl21.pdk` plug-ins.

- [Sky130](./Sky130) serves the [SkyWater 130nm](https://github.com/google/skywater-pdk) technology
- [Asap7](./Asap7) serves the [ASAP7](https://github.com/The-OpenROAD-Project/asap7/) predictive/ academic technology
- [SamplePdk](./SamplePdk) is a purely contrived technology, demonstrating bare-minimum creation of Mos transistors and replacement of `hdl21.Primitive` elements

While source-controlled in the Hdl21 codebase, each are stand-alone packages,
distributed through PyPi and revision-managed with [Poetry](https://python-poetry.org/docs/).
