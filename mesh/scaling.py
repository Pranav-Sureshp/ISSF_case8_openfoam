import sys
import numpy as np

sys.path.append(r"/home/pranav/repos/nekrs_mhd_examples/python")
import nekrs_mhd_calc as calc

density_f = 9838.01
dyn_viscosity_f = 2.108e-3
elec_conductivity_f = 8.835e5
thermal_conductivity_f = 20.40
spec_heat_cap_f = 189.8
thermal_expansion_coeff_f = 1.21e-4

elec_conductivity_s = 1.09e6
thermal_conductivity_s = 19.0
spec_heat_cap_s = 500.0


a = 23 / 1000  # duct interior half-size in direction parallel to B
b = a  # duct interior half-size in direction perpendicular to B
d = 3  # duct length
t_w = 2 / 1000  # wall thickness
U = 0.03
Bfield_mag = 0.5
Bfield_orientation = (0, 1, 0)

gravity_mag = 9.81
gravity_orientation = (0, 0, -1)

heat_flux = 0.04e6

ref_temp = 573
max_temp = ref_temp + heat_flux*a/thermal_conductivity_f

permeability = 4e-7 * np.pi

case = calc.NekRescaleMHD(
    U,
    Bfield_mag,
    Bfield_orientation,
    a,
    density_f,
    dyn_viscosity_f,
    permeability,
    elec_conductivity_f,
    elec_conductivity_s,
    ref_length_is_mhd=True,
    ref_viscosity_is_dynamic=True,
    inductionless_NJxB=True,
    energy_equation=True,
    ref_temperature=ref_temp,
    upper_temperature=max_temp,
    ref_specific_heat_capacity=spec_heat_cap_f,
    ref_thermal_conductivity=thermal_conductivity_f,
    boussinesq_buoyancy=True,
    ref_gravitational_acceleration_magnitude=gravity_mag,
    ref_gravitational_acceleration_orientation=gravity_orientation,
    ref_thermal_expansion_coeff=thermal_expansion_coeff_f,
)
case.print_scaling_summary()
case.par_inputs()
