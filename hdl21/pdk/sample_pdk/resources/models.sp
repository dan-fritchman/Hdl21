
* # Sample PDK Models
* 
* A pair of NMOS and PMOS, equal to the default BSIM4 models. 
* Each are exposed both as subcircuits ("x-elements") named `nmos` and `pmos`, 
* and SPICE models ("m-elements") named `nmos_model` and `pmos_model`.
* 

* The model-based version
.model nmos_model nmos level=54

* The subcircuit-based version
.subckt nmos  d g s b  l='1u' w='1u' nf='1' m='1'
  mn d g s b nmos_model l='l' w='w' nf='nf' m='m'
.ends 

* The model-based version
.model pmos_model pmos level=54

* The subcircuit-based version
.subckt pmos  d g s b  l='1u' w='1u' nf='1' m='1'
  mp d g s b pmos_model l='l' w='w' nf='nf' m='m'
.ends 
