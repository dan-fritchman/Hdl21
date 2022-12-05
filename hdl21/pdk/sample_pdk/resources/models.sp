
* # Sample PDK Models
* 
* Equal to the default BSIM4 models
* 
* Note these *are not* parametric! 
* This file is syntactically generic-enough to work in all our favorite simulators; 
* passing parameters hierarchically would require a different syntax for each simulator.


.subckt nmos d g s b
  .model nmos_model nmos level=54
  mn d g s b nmos_model l=1u w=1u nf=1
.ends 

.subckt pmos d g s b
  .model pmos_model pmos level=54
  mp d g s b pmos_model l=1u w=1u nf=1
.ends 
