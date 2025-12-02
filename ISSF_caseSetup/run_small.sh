#!/bin/bash
# Source the OpenFOAM profile

ulimit -s unlimited

cores=32
solver=epotFoam_isoTh #epotFoam_isoTh  # cEpotmhdEpotMultiRegionFoam
source ~/.openfoam_v2206_profile
#blockMesh   2>&1 | tee log.blockMesh_fluid
#blockMesh -region walls  2>&1 | tee log.blockMesh_walls
./fluentmeshTofoam

