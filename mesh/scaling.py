import sys
import numpy as np

sys.path.append(r"../nekrs_mhd_examples/python")
import nekrs_mhd_calc as calc

density = 9838.01
viscosity = 2.108e-3
conductivity_f = 8.835e5
conductivity_s = 1.09e6
a = 23/1000       # duct interior half-size in direction parallel to B
b = a               # duct interior half-size in direction perpendicular to B
d = 3               # duct length
t_w = 2/1000        # wall thickness
U = 0.03
Bfield_mag = 0.5
Bfield_orientation = (0, 1, 0)
permeability = 4e-7*np.pi

case = calc.NekRescaleMHD(
    U, Bfield_mag, Bfield_orientation, a, density, viscosity, permeability, conductivity_f,conductivity_s,True,True)
case.print_scaling_summary()
case.par_inputs()

#------------------------------------------------------------------------------

# Mesh parameters
HL = a / case.Ha  # Hartmann layer
SL = a / case.Ha**0.5  # Side layer

# First layer thickness
FLT = 1 * HL

# Boundary layer total thickness
BL = 5 * SL

# Growth rate
gr = 1.15

# Number of layers
Num_of_layers = np.ceil(np.log(1 - (BL * (1 - gr)) / FLT) / np.log(gr))

# Nth Layer Thickness 
Nth_layer=FLT*gr**(Num_of_layers-1)

# Suggested face sizing based on last layer of inflation (2*Nth LT)
Face_sz = Nth_layer

# Number of layers on solid region
Num_of_layers_solid = np.floor(np.log(1 - (t_w * (1 - gr)) / FLT) / np.log(gr))


# Print all parameters
print(f"Hartmann Layer Thickness (HL): {HL:.6e} m")
print(f"Side Layer Thickness (SL): {SL:.6e} m")
print(f"First Layer Thickness (FLT): {FLT:.6e} m")
print(f"Boundary Layer Total Thickness (BL): {BL:.6e} m")
print(f"Growth Rate (gr): {gr:.2f}")
print(f"Number of Layers: {int(Num_of_layers)}")
print(f"Nth Layer Thickness: {Nth_layer:.6e} m")
print(f"Suggested Face Sizing (Face_sz): {Face_sz:.6e} m")
print(f"Number of Layers in the solid region: {int(Num_of_layers_solid)}")
#-----------------------------------------------------------------------------
L_x_fluid = 2*a
L_y_fluid = 2*b
L_z_fluid = d
L_x_solid = L_x_fluid + 2*t_w
L_y_solid = L_y_fluid + 2*t_w
L_z_solid = L_z_fluid


# Set mesh parameters as for a low-order mesh

lo_delta_xy_core = Face_sz
lo_delta_z_axial = 0.2*a

lo_fluid_first_row = FLT
lo_fluid_growth_factor = gr
lo_fluid_num_layers = Num_of_layers
lo_solid_first_row = FLT
lo_solid_growth_factor = gr
lo_solid_num_layers = Num_of_layers_solid

print("\n--- Fluid and Solid Domain Dimensions ---")
print(f"L_x_fluid (Fluid domain length in x-direction): {L_x_fluid:.6e} m")
print(f"L_y_fluid (Fluid domain length in y-direction): {L_y_fluid:.6e} m")
print(f"L_z_fluid (Fluid domain length in z-direction): {L_z_fluid:.6e} m")
print(f"L_x_solid (Solid domain length in x-direction): {L_x_solid:.6e} m")
print(f"L_y_solid (Solid domain length in y-direction): {L_y_solid:.6e} m")
print(f"L_z_solid (Solid domain length in z-direction): {L_z_solid:.6e} m")

# Print low-order mesh parameters
print("\n--- Low-Order Mesh Parameters ---")
print(f"Core xy-plane mesh size (lo_delta_xy_core): {lo_delta_xy_core:.6e} m")
print(f"Axial direction mesh size (lo_delta_z_axial): {lo_delta_z_axial:.6e} m")

print(f"Fluid first row thickness (lo_fluid_first_row): {lo_fluid_first_row:.6e} m")
print(f"Fluid growth factor (lo_fluid_growth_factor): {lo_fluid_growth_factor:.2f}")
print(f"Fluid number of layers (lo_fluid_num_layers): {int(lo_fluid_num_layers)}")

print(f"Solid first row thickness (lo_solid_first_row): {lo_solid_first_row:.6e} m")
print(f"Solid growth factor (lo_solid_growth_factor): {lo_solid_growth_factor:.2f}")
print(f"Solid number of layers (lo_solid_num_layers): {int(lo_solid_num_layers)}")
