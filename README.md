# ISSF Case Study 8: LM-MHD in nonuniform magnetic fields and subject to external heating

The case is summarised as follows:

- Flow in $x$ direction
- Square duct ($b=a$)
- Heat $q''$ applied at $z=-25{\rm\,mm}$ (bottom wall) for $-0.3{\rm\,m}<x<0.3{\rm\,m}$
- Gravity acts in $-z$ direction
- MHD: Inductionless approximation
- Buoyancy: Boussinesq approximation
- Nonuniform magnetic field: $\vec{B} = \left(0, B_y(x), 0\right)$, where

```math
B_y(x) = \frac{1}{2}B_0\left(1-\tanh\left(\frac{|x|-0.7315}{0.1} \right)\right)
```

## Reference values

| Property | Symbol | Value | Units
| -- | -- | -- | -- |
| Half-width | $a$ | $23$ | $\rm mm$ |
| Axial length | $d$ | $3$ | $\rm m$ |
| Uniform wall thickness | $t_w$ | $2$ | $\rm mm$ |
| Uniform inlet temperature | T_in | $300$ | $\rm\degree C$ |
| Applied heat flux | $q''$ | $0.04$ | $\rm MW\cdot m^{-2}$ |
| Peak field strength | $B_0$ | $0.5$ | $\rm T$ |
| Uniform inlet velocity | $u_{inlet}$ | $0.03$ | $\rm m\cdot s^{-1}$ |
| Hartmann number | $\rm Ha$ | $235.43$ | ND |
| Reynolds number | $\rm Re$ | $3220.22$ | ND |
| Grashof number | $\rm Gr$ | $1.419\times10^7$ | ND |
| Richardson number | $\rm Ri$ | $1.368$ | ND |

## Material properties

| Property |  Unit | PbLi | Stainless Steel |
| -- | -- | -- | -- |
| Density | $\rm kg \cdot m^{-3}$ | $9838.01$ | $7800$ |
| Dynamic viscosity | $\rm kg \cdot m^{-1} \cdot s^{-1}$ | $2.108\times10^-3$ | - |
| Electric conductivity | $\rm S \cdot m^{-1} $ | $8.835\times10^5$ | $1.09\times10^6$ |
| Specific heat capacity | $\rm J\cdot kg^{-1}\cdot K^{-1}$ | $189.8$ | $500$ |
| Thermal conductivity | $\rm W\cdot m^{-1}\cdot K^{-1}$ | $20.40$ | $19.0$ |
| Volumetric expansion coefficient | $\rm K^{-1}$ | $1.210\times10^{-4}$ | - |

# Geometry

Surfaces defined in exodus mesh:

1. Inlet
2. Outlet
3. Fluid-solid interface
4. Exterior minus heated patch
5. Heated patch