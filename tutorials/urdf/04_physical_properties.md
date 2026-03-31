# 04 — Physical and Collision Properties

To use a robot model in a physics simulator (Gazebo), every link needs two additional elements beyond `<visual>`:

- `<collision>` — geometry used for contact detection
- `<inertial>` — mass and inertia tensor for dynamics

## Collision Geometry

The `<collision>` element has the same structure as `<visual>` but defines the shape used by the physics engine for contact calculations. It is kept **separate from visual geometry** to allow deliberate simplification.

```xml
<link name="base_link">

  <!-- Visual: detailed mesh for rendering -->
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <mesh filename="package://my_robot_description/meshes/base_link.STL"/>
    </geometry>
    <material name="blue"/>
  </visual>

  <!-- Collision: simplified cylinder for fast contact detection -->
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.15" length="0.08"/>
    </geometry>
  </collision>

</link>
```

### When to Simplify Collision Geometry

| Situation | Recommended Approach |
|-----------|---------------------|
| Complex mesh with many polygons | Replace with a primitive (box, cylinder, sphere) |
| Safety-critical zone around a component | Enlarge the collision geometry beyond visual bounds |
| Flat ground plane | Use a thin box covering the expected area |
| Wheel in contact with ground | Use a sphere or thin cylinder matching actual radius |

## Inertial Properties

Every link that participates in physics simulation **must** have an `<inertial>` element. Without it, Gazebo assigns zero mass and the simulation becomes unstable.

```xml
<link name="base_link">
  <inertial>
    <!-- Center of mass relative to the link origin -->
    <origin xyz="0 0 0.04" rpy="0 0 0"/>

    <!-- Total mass in kilograms -->
    <mass value="0.8257"/>

    <!-- Inertia tensor (symmetric 3×3 matrix) in kg·m² -->
    <inertia
      ixx="2.2124e-02" ixy="-1.2294e-04" ixz="3.4938e-04"
                        iyy="2.1193e-02"  iyz="-5.0120e-05"
                                           izz="2.0064e-02"/>
  </inertial>
  <!-- ... visual and collision ... -->
</link>
```

### The Inertia Tensor

The inertia tensor $\mathbf{I}$ is a $3 \times 3$ symmetric matrix:

$$
\mathbf{I} =
\begin{pmatrix}
I_{xx} & I_{xy} & I_{xz} \\
I_{xy} & I_{yy} & I_{yz} \\
I_{xz} & I_{yz} & I_{zz}
\end{pmatrix}
$$

- **Diagonal elements** ($I_{xx}$, $I_{yy}$, $I_{zz}$): moments of inertia around each axis
- **Off-diagonal elements** ($I_{xy}$, $I_{xz}$, $I_{yz}$): products of inertia (zero if geometry is symmetric about each axis)

### Inertia Formulas for Common Primitives

For a **solid cylinder** (mass $m$, radius $r$, length $h$, axis along Z):

$$
I_{xx} = I_{yy} = \frac{m}{12}(3r^2 + h^2), \quad I_{zz} = \frac{m r^2}{2}
$$

For a **solid box** (mass $m$, dimensions $d_x \times d_y \times d_z$):

$$
I_{xx} = \frac{m}{12}(d_y^2 + d_z^2), \quad
I_{yy} = \frac{m}{12}(d_x^2 + d_z^2), \quad
I_{zz} = \frac{m}{12}(d_x^2 + d_y^2)
$$

For a **solid sphere** (mass $m$, radius $r$):

$$
I_{xx} = I_{yy} = I_{zz} = \frac{2mr^2}{5}
$$

> **Tip:** For simple models, use the primitive formulas above. For complex mesh-based links, use a CAD tool or online inertia calculator. Avoid the identity matrix (`ixx=iyy=izz=1`), as it represents an unrealistic mass distribution.

## Joint Dynamics

Add dynamics properties to movable joints to model friction and damping:

```xml
<joint name="wheel_right_joint" type="continuous">
  <parent link="base_link"/>
  <child  link="wheel_right_link"/>
  <origin xyz="0 -0.07 0" rpy="0 0 0"/>
  <axis   xyz="0 1 0"/>

  <dynamics
    damping="0.01"   <!-- N·m·s/rad for revolute/continuous, N·s/m for prismatic -->
    friction="0.1"/> <!-- N·m for revolute/continuous, N for prismatic -->
</joint>
```

| Property | Unit (revolute) | Unit (prismatic) | Meaning |
|----------|----------------|-----------------|---------|
| `damping` | N·m·s/rad | N·s/m | Velocity-proportional resistive force |
| `friction` | N·m | N | Constant resistive force at rest |

## Contact Coefficients

For links that make contact with the environment (wheels, feet), add contact properties inside the `<collision>` element:

```xml
<link name="wheel_right_link">
  <collision>
    <origin xyz="0 0 0" rpy="1.5708 0 0"/>
    <geometry>
      <sphere radius="0.033"/>
    </geometry>
    <contact_coefficients
      mu="0.8"    <!-- Coulomb friction coefficient -->
      kp="1e6"   <!-- Contact stiffness (N/m) -->
      kd="1.0"   <!-- Contact damping (N·s/m) -->
    />
  </collision>
</link>
```

## Complete Link with All Properties

This is a complete link definition for a differential drive wheel, suitable for physics simulation:

```xml
<link name="wheel_right_link">

  <inertial>
    <origin xyz="0 -0.014 0" rpy="0 0 0"/>
    <mass value="0.0530"/>
    <inertia
      ixx="1.8817e-05" ixy="-4.8444e-10" ixz="1.8816e-08"
                        iyy="3.1151e-05"  iyz="-6.9356e-11"
                                           izz="1.8801e-05"/>
  </inertial>

  <visual>
    <origin xyz="0 0 0" rpy="1.5708 0 0"/>
    <geometry>
      <mesh filename="package://my_robot_description/meshes/wheel_right_link.STL"/>
    </geometry>
    <material name="dark"/>
  </visual>

  <!-- Use sphere for collision: simpler, better ground contact behavior -->
  <collision>
    <origin xyz="0 -0.015 0" rpy="1.5708 0 0"/>
    <geometry>
      <sphere radius="0.033"/>
    </geometry>
    <contact_coefficients mu="0.8" kp="1e6" kd="1.0"/>
  </collision>

</link>
```

## Continuous Joint with Dynamics

```xml
<joint name="wheel_right_joint" type="continuous">
  <parent link="base_link"/>
  <child  link="wheel_right_link"/>
  <origin xyz="0 -0.0701 0" rpy="0 0 0"/>
  <axis   xyz="0 1 0"/>
  <dynamics damping="0.01" friction="0.1"/>
</joint>
```

## Inertia Helper Script

Rather than computing inertia tensors by hand, use this Python snippet for common primitives:

```python
#!/usr/bin/env python3
"""Inertia tensor calculator for URDF primitives."""
import math


def cylinder_inertia(mass: float, radius: float, length: float) -> dict:
    """Solid cylinder with axis along Z."""
    ixx = iyy = (mass / 12.0) * (3 * radius**2 + length**2)
    izz = 0.5 * mass * radius**2
    return {"ixx": ixx, "iyy": iyy, "izz": izz, "ixy": 0, "ixz": 0, "iyz": 0}


def box_inertia(mass: float, dx: float, dy: float, dz: float) -> dict:
    """Solid box with dimensions dx × dy × dz."""
    ixx = (mass / 12.0) * (dy**2 + dz**2)
    iyy = (mass / 12.0) * (dx**2 + dz**2)
    izz = (mass / 12.0) * (dx**2 + dy**2)
    return {"ixx": ixx, "iyy": iyy, "izz": izz, "ixy": 0, "ixz": 0, "iyz": 0}


def sphere_inertia(mass: float, radius: float) -> dict:
    """Solid sphere."""
    i = (2.0 / 5.0) * mass * radius**2
    return {"ixx": i, "iyy": i, "izz": i, "ixy": 0, "ixz": 0, "iyz": 0}


def print_urdf_inertia(d: dict) -> None:
    print(
        f'<inertia ixx="{d["ixx"]:.6e}" ixy="{d["ixy"]:.6e}" '
        f'ixz="{d["ixz"]:.6e}"\n'
        f'          iyy="{d["iyy"]:.6e}" iyz="{d["iyz"]:.6e}"\n'
        f'                                 izz="{d["izz"]:.6e}"/>'
    )


# Example: wheel (cylinder, axis along Y — so swap ixx and izz)
wheel = cylinder_inertia(mass=0.053, radius=0.033, length=0.026)
print("Wheel inertia:")
print_urdf_inertia(wheel)
```

Save as `scripts/inertia_calculator.py` and run with `python3 scripts/inertia_calculator.py`.

## Checklist Before Simulating

- [ ] Every simulated link has `<inertial>` with non-zero mass
- [ ] No link has zero or identity inertia (`ixx=iyy=izz=1`)
- [ ] Collision geometry is present for every link that should make contact
- [ ] Wheel collision uses sphere or cylinder matching actual wheel radius
- [ ] Joint dynamics are set for movable joints
- [ ] Inertia origin matches the actual center of mass

## Next Steps

Proceed to [05 — Using Xacro](05_xacro.md) to eliminate code duplication and make your URDF maintainable.
