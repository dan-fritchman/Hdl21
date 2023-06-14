
# Hdl21 Sample PDK

A non-physical, 110% made-up process technology, designed solely for demonstrating the `hdl21.pdk` interface. 
The Hdl21 sample PDK is integrated in the Hdl21 package, and is therefore available to every installation of Hdl21. 

It includes: 
* Nmos and Pmos transistor `ExternalModule`s
* Similar transistor modules, defined as SPICE primitive-MOS models
* Comilation from `hdl21.primitives` to the PDK modules 
* An `Install` type, demonstrating typical usage of out-of-Python PDK installation data 
* A built-in model file, compatible with all supported simulators

Note that unlike most Hdl21 PDKs, the content of `sample_pdk.install` - the model file - 
*is* built into the source tree, and is configured at import-time. 
For most PDKs in which this data is distributed separately, 
a site-specific `sitepdks` module customarily configures the `install` variable.
