import cubit
import sys
import numpy as np

sys.path.append("../nekrs_mhd_examples/python")
import boundary_layer_high_order_convert as bl

cubit.cmd('reset')

### User Settings ###

# Set exodus file names
meshname_fluid = "fluid_submap"
meshname_solid = "solid_submap"

high_order = True
if high_order:
  polynomial_order = 7
  first_layer_multiplier = 0.5
  num_qps_in_first_layer = 1
  meshname_fluid = meshname_fluid + "_nekRS"
  meshname_solid = meshname_solid + "_nekRS"
else:
  polynomial_order = 1
  first_layer_multiplier = 1/7
  num_qps_in_first_layer = 1
  meshname_fluid = meshname_fluid + "_OpenFOAM"
  meshname_solid = meshname_solid + "_OpenFOAM"

# Set reference length for nondimensionalisation
# Applied after mesh generation
ref_length = 23/1000

# Set geometry parameters
# Note on orientation:
# u_in=(0,0,u_in)
# B_0=(B_0,0,0)
# need to rotate!!!

Ha = 235.43217457163624
a = 23/1000     # duct interior half-size in direction parallel to B
b = a           # duct interior half-size in direction perpendicular to B
d = 3           # duct length
t_w = 2/1000    # duct wall thickness

heater_len = 0.6

L_x_fluid = 2*a
L_y_fluid = 2*b
L_z_fluid = d
L_x_solid = L_x_fluid + 2*t_w
L_y_solid = L_y_fluid + 2*t_w
L_z_solid = L_z_fluid

# Set mesh parameters as for a low-order mesh

axial_mesh_size = 0.2*a

# Mesh parameters
HL = a / Ha  # Hartmann layer
SL = a / Ha**0.5  # Side layer

# First layer thickness
FLT = first_layer_multiplier * HL

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

lo_delta_xy_core = Face_sz
lo_delta_z_axial = axial_mesh_size

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

# Convert mesh parameters to the coarser settings required
# for a comparable high-order mesh

fluid_first_row, fluid_growth_factor, fluid_num_layers = bl.boundary_layer_low_to_high_order(lo_fluid_first_row, lo_fluid_growth_factor, lo_fluid_num_layers, polynomial_order, num_qps_in_first_layer)[0]
solid_first_row, solid_growth_factor, solid_num_layers = bl.boundary_layer_low_to_high_order(lo_solid_first_row, lo_solid_growth_factor, lo_solid_num_layers, polynomial_order, num_qps_in_first_layer)[0]

solid_num_layers = solid_num_layers - 1 # prevent overconstrained final layer

delta_xy_core = lo_delta_xy_core * polynomial_order
delta_z_axial = lo_delta_z_axial * polynomial_order

### Generate Geometry ###

cubit.cmd(f'brick x {L_x_fluid} y {L_y_fluid} z {L_z_fluid}') # fluid region
cubit.cmd(f'brick x {L_x_solid} y {L_y_solid} z {L_z_solid}') # solid+fluid region
cubit.cmd('subtract volume 1 from volume 2 keep_tool') # create solid-only region

# Webcut solid region to separate corners

cubit.cmd('webcut volume 2 with plane from surface 14')
cubit.cmd('webcut volume 2 with plane from surface 16')
cubit.cmd('webcut volume 2 3 with plane from surface 15')
cubit.cmd('webcut volume 2 3 with plane from surface 13')

# Imprint and merge
cubit.cmd('imprint volume all') # imprint
cubit.cmd('merge volume all') # merge
cubit.cmd('compress') # minimise all ID numbers

# Create surface object for heated patch

cubit.cmd(f'brick x {L_x_solid} y {L_y_solid} z {heater_len}')

# Rotate to align with coordinate system
cubit.cmd('rotate volume all angle 90 about y include_merged')

# Note, at this point:
# Centroid is at (0,0,0)
# Volume 1    = fluid region
# Volume 2-9  = solid region
# Surface 1   = fluid outlet
# Surface 2   = fluid inlet
# Surface 3   = y=-b fluid-solid interface (Hartmann wall)
# Surface 4   = z=-a fluid-solid interface (side wall)
# Surface 5   = y=+b fluid-solid interface (Hartmann wall)
# Surface 6   = z=+a fluid-solid interface (side wall)
# Surface 9 12 20   = y=-b-t_w exterior surface
# Surface 26 39 40  = z=+a+t_w exterior surface
# Surface 10 15 19  = y=+b+t_w exterior surface
# Surface 22 32 33   = z=-a-t_w exterior surface
# Surface 13 16 24 27 31 34 37 42 = solid outlet
# Surface 14 17 23 28 30 35 38 41 = solid inlet

# Imprint and merge
cubit.cmd('imprint volume all') # imprint
cubit.cmd('merge volume all') # merge
cubit.cmd('delete volume 10')

# Now IDs for everything except fluid + solid inlet + outlet have changed
# Surface 75 76 84 121 122 130 145 146 154 = z=+a+t_w exterior surface
# Surface 63 72 111 112 133 134 = z=-a-t_w exterior surface excluding heater
# Surface 64 118 142 = z=-a-t_w heated patch
# Surface 103 104 106 115 116 119 125 126 132 = y=+a+t_w exterior surface
# Surface 87 88 94 137 138 144 149 150 156 = y=-a-t_w exterior surface
# Surface 55 56 57 = y=-a fluid-solid interface (Hartmann wall)
# Surface 49 50 59 = y=+a fluid-solid interface (Hartmann wall)
# Surface 51 52 60 = z=-a fluid-solid interface (side wall)
# Surface 53 54 58 = z=+a fluid-solid interface (side wall)

### Create named sidesets ###

# create named sidesets

cubit.cmd('sideset 1 add surface 2')
cubit.cmd('sideset 1 name "fluid_inlet"')
cubit.cmd('sideset 2 add surface 1')
cubit.cmd('sideset 2 name "fluid_outlet"')
cubit.cmd('sideset 3 add surface 49 50 51 52 53 54 55 56 57 58 59 60')
cubit.cmd('sideset 3 name "fs_interface"')
cubit.cmd('sideset 4 add surface 75 76 84 121 122 130 145 146 154')
cubit.cmd('sideset 4 add surface 63 72 111 112 133 134')
cubit.cmd('sideset 4 add surface 103 104 106 115 116 119 125 126 132')
cubit.cmd('sideset 4 add surface 87 88 94 137 138 144 149 150 156')
cubit.cmd('sideset 4 name "exterior"')
cubit.cmd('sideset 5 add surface 14 17 23 28 30 35 38 41')
cubit.cmd('sideset 5 name "solid_inlet"')
cubit.cmd('sideset 6 add surface 13 16 24 27 31 34 37 42')
cubit.cmd('sideset 6 name "solid_outlet"')
cubit.cmd('sideset 7 add surface 64 118 142')
cubit.cmd('sideset 7 name "heater"')

# # ### Set up boundary layers ###

# Create Hartmann layer in fluid region
cubit.cmd('create boundary_layer 1')
cubit.cmd(f'modify boundary_layer 1 uniform height {fluid_first_row} growth {fluid_growth_factor} layers {fluid_num_layers}')
cubit.cmd('modify boundary_layer 1 add surface 51 52 60 volume 1')
cubit.cmd('modify boundary_layer 1 add surface 53 54 58 volume 1')
cubit.cmd('modify boundary_layer 1 add surface 61 62 67 68 69 71 volume 2')
cubit.cmd('modify boundary_layer 1 add surface 73 74 79 80 81 83 volume 3')
cubit.cmd('modify boundary_layer 1 continuity off')

# Create side layer in fluid region
cubit.cmd('create boundary_layer 2')
cubit.cmd(f'modify boundary_layer 2 uniform height {fluid_first_row} growth {fluid_growth_factor} layers {fluid_num_layers}')
cubit.cmd('modify boundary_layer 2 add surface 55 56 57 volume 1')
cubit.cmd('modify boundary_layer 2 add surface 49 50 59 volume 1')
cubit.cmd('modify boundary_layer 2 add surface 85 86 91 92 93 95 volume 4')
cubit.cmd('modify boundary_layer 2 add surface 99 100 101 102 107 108 volume 5')
cubit.cmd('modify boundary_layer 2 continuity off')

# Create Hartmann layer in solid region
cubit.cmd('create boundary_layer 3')
cubit.cmd(f'modify boundary_layer 3 uniform height {solid_first_row} growth {solid_growth_factor} layers {solid_num_layers}')
cubit.cmd('modify boundary_layer 3 add surface 51 52 60 volume 2')
cubit.cmd('modify boundary_layer 3 add surface 53 54 58 volume 3')
cubit.cmd('modify boundary_layer 3 add surface 101 102 108 volume 6')
cubit.cmd('modify boundary_layer 3 add surface 99 100 107 volume 7')
cubit.cmd('modify boundary_layer 3 add surface 91 92 93 volume 8')
cubit.cmd('modify boundary_layer 3 add surface 85 86 95 volume 9')
cubit.cmd('modify boundary_layer 3 continuity off')

# Create side layer in solid region
cubit.cmd('create boundary_layer 4')
cubit.cmd(f'modify boundary_layer 4 uniform height {solid_first_row} growth {solid_growth_factor} layers {solid_num_layers}')
cubit.cmd('modify boundary_layer 4 add surface 49 50 59 volume 5')
cubit.cmd('modify boundary_layer 4 add surface 55 56 57 volume 4')
cubit.cmd('modify boundary_layer 4 add surface 61 62 71 volume 6')
cubit.cmd('modify boundary_layer 4 add surface 73 74 83 volume 7')
cubit.cmd('modify boundary_layer 4 add surface 67 68 69 volume 8')
cubit.cmd('modify boundary_layer 4 add surface 79 80 81 volume 9')
cubit.cmd('modify boundary_layer 4 continuity off')

### Generate Mesh ###

# create element blocks
cubit.cmd('block 1 add volume 1')
cubit.cmd('block 2 add volume 2 to 9')

if high_order:
  # set element type
  cubit.cmd('block 1 element type hex20')
  cubit.cmd('block 2 element type hex20')

# Set mesh size for axial resolution (on all volumes)

cubit.cmd(f'volume all size {delta_z_axial}')

# Set approximate mesh size for fluid core (on inlet surface)

cubit.cmd(f'surface 2 size {delta_xy_core}')

# Set approximate mesh size for solid (on solid inlet surface)
cubit.cmd(f'surface 14 17 23 28 30 35 38 41 size {delta_xy_core}')

# Mesh fluid inlet

cubit.cmd('surface 2 submap smooth off')
cubit.cmd('surface 2 scheme submap')
cubit.cmd('mesh surface 2')

# Mesh solid inlet

cubit.cmd('surface 14 17 23 28 30 35 38 41 submap smooth off')
cubit.cmd('surface 14 17 23 28 30 35 38 41 scheme submap')
cubit.cmd('mesh surface 14 17 23 28 30 35 38 41')

# Sweep mesh through volume

# defaults to sweep
cubit.cmd('mesh volume 1')
cubit.cmd('mesh volume 2 to 9')

### Nondimensionalise geometry and mesh length scale ###

cubit.cmd(f'volume all scale {1.0/ref_length}')

### Save mesh (exodus) ###

cubit.cmd('set exodus netcdf4 off')
cubit.cmd('set large exodus file on')
cubit.cmd(f'export mesh "{meshname_fluid}.exo" block 1 overwrite')
cubit.cmd(f'export mesh "{meshname_solid}.exo" block 2 overwrite')
