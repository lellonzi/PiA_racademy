# Chapter 2 What Is URDF?

**U**nified **R**obot **D**escription **F**ormat (URDF) is an XML dialect used across ROS to model a robot’s physical structure. In its simplest form a URDF file answers three questions:

| **Concept**  | **URDF Element**        | **What it encodes**                                                                        |
| ------------ | ----------------------- | ------------------------------------------------------------------------------------------ |
| _Rigid body_ | `<link>`                | Visual and collision geometry of a single, non-deformable part.                            |
| _Connection_ | `<joint>`               | How two links move relative to one another (fixed, revolute, continuous, prismatic, etc.). |
| _Hierarchy_  | Parent/child attributes | The tree structure that defines the robot’s kinematic chain.                               |

URDF files can become verbose, so ROS provides **xacro** (XML Macros) to enable variables, includes, and loops. A file ending in `.urdf.xacro` must be _expanded_ into plain URDF at launch time, but otherwise follows the same rules.

---

## 2 Creating a _description_ Package

A dedicated package keeps meshes, URDF, and textures neatly together.

```bash
# Inside your workspace root
$ cd src/
$ ros2 pkg create --build-type ament_cmake racademy_description
$ cd ..
$ colcon build
```

Why `ament_cmake`? Although the package itself holds only data, we will rely on CMake’s install rules to copy those assets into the _install space_ where other packages can find them.

Directory layout (after we add files):

```text
<your_github_repo>/
└── racademy_ws/
    └── src/
        └── racademy_description/
            ├── meshes/           # STL, DAE, COLLADA, PNG, ...
            └── urdf/
                └── racademy.urdf.xacro
```

---

## 3 Authoring `racademy.urdf.xacro`

Create _`<your_github_repo>/racademy_ws/src/racademy_description/urdf/racademy.urdf.xacro`_ and paste the listing below. Each line is numbered so we can dissect it afterwards.

```xml
<?xml version="1.0"?>                                         <!--  1 -->

<robot xmlns:xacro="http://www.ros.org/wiki/xacro"            <!--  2 -->
       name="racademy">

  <xacro:property name="wheel_offset_y" value="0.07"/>        <!--  3 -->
  <xacro:property name="base_height" value="0.033"/>          <!--  4 -->

  <!--  A.  Base frames  -->
  <link name="base_footprint"/>                               <!--  5 -->

  <link name="base_link">                                     <!--  6 -->
    <visual>                                                  <!--  7 -->
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!--  8 -->
      <geometry>                                              <!--  9 -->
        <mesh filename="package://racademy_description/meshes/duckiebotFrame.dae"/><!-- 10 -->
      </geometry>
    </visual>
    <collision>                                               <!-- 11 -->
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!-- 12 -->
      <geometry>                                              <!-- 13 -->
        <mesh filename="package://racademy_description/meshes/duckiebotFrame.dae"/><!-- 14 -->
      </geometry>
    </collision>
  </link>

  <joint name="base_joint" type="fixed">                      <!-- 15 -->
    <parent link="base_footprint"/>                           <!-- 16 -->
    <child  link="base_link"/>                                <!-- 17 -->
    <origin xyz="0 0 ${base_height}" rpy="0 0 0"/>           <!-- 18 -->
  </joint>

  <!--  B.  Left wheel  -->
  <link name="left_wheel_link">                               <!-- 19 -->
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!-- 20 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_leftwheel.dae"/><!-- 21 -->
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!-- 22 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_leftwheel.dae"/><!-- 23 -->
      </geometry>
    </collision>
  </link>

  <joint name="left_wheel_joint" type="continuous">           <!-- 24 -->
    <origin xyz="0 ${wheel_offset_y} 0" rpy="0 0 0"/>        <!-- 25 -->
    <parent link="base_link"/>                                <!-- 26 -->
    <child  link="left_wheel_link"/>                          <!-- 27 -->
    <axis xyz="0 1 0"/>                                       <!-- 28 -->
  </joint>

  <!--  C.  Right wheel  -->
  <link name="right_wheel_link">                              <!-- 29 -->
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!-- 30 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_rightwheel.dae"/><!-- 31 -->
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!-- 32 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_rightwheel.dae"/><!-- 33 -->
      </geometry>
    </collision>
  </link>

  <joint name="right_wheel_joint" type="continuous">          <!-- 34 -->
    <origin xyz="0 -${wheel_offset_y} 0" rpy="0 0 0"/>       <!-- 35 -->
    <parent link="base_link"/>                                <!-- 36 -->
    <child  link="right_wheel_link"/>                         <!-- 37 -->
    <axis xyz="0 1 0"/>                                       <!-- 38 -->
  </joint>

  <!--  D.  Computer  -->
  <link name="computer_link">                                 <!-- 39 -->
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!-- 40 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_computer.dae"/><!-- 41 -->
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>                      <!-- 42 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_computer.dae"/><!-- 43 -->
      </geometry>
    </collision>
  </link>

  <joint name="computer_joint" type="fixed">                  <!-- 44 -->
    <parent link="base_link"/>                                <!-- 45 -->
    <child  link="computer_link"/>                            <!-- 46 -->
    <origin xyz="0 0 0" rpy="0 0 0"/>                        <!-- 47 -->
  </joint>

  <!--  E.  Camera  -->
  <link name="camera_link">                                   <!-- 48 -->
    <visual>
      <origin xyz="-0.05 0 -0.055" rpy="0 -0.1 0"/>          <!-- 49 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_camera.dae"/><!-- 50 -->
      </geometry>
    </visual>
    <collision>
      <origin xyz="-0.05 0 -0.055" rpy="0 -0.1 0"/>          <!-- 51 -->
      <geometry>
        <mesh filename="package://racademy_description/meshes/duckiebot_camera.dae"/><!-- 52 -->
      </geometry>
    </collision>
  </link>

  <joint name="camera_joint" type="fixed">                    <!-- 53 -->
    <parent link="base_link"/>                                <!-- 54 -->
    <child  link="camera_link"/>                              <!-- 55 -->
    <origin xyz="0.05 0 0.05" rpy="0 0.1 0"/>                <!-- 56 -->
  </joint>

</robot>
```

### 3.1 Line-by-Line Explanation

| **Line(s)** | **Purpose**                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1           | Standard XML declaration—always start URDF/xacro files with this.                                                                                                                                                                                                                           |
| 2           | `<robot>` root element; `xmlns:xacro` enables macro syntax; the `name` attribute tags every TF frame with a common prefix.                                                                                                                                                                  |
| 3–4         | `xacro:property` definitions create reusable constants for wheel placement and base height so dimensions can be edited in one place.                                                                                                                                                        |
| 5           | `base_footprint` frame lies flat on the ground; many navigation stacks expect it.                                                                                                                                                                                                           |
| 6–14        | `base_link` represents the robot’s rigid chassis. The nested `<visual>` contains display geometry, while `<collision>` defines geometry used for collision checking. Lines 10 and 14 reference the chassis mesh via the _package URI_ syntax so that paths remain valid after installation. |
| 15–18       | A **fixed joint** welds `base_footprint` to `base_link`. Line 18 offsets the frame upward by 33 mm so that the footprint sits flush with the floor while the model body is elevated above it.                                                                                               |
| 19–23       | `left_wheel_link` holds the visual and collision mesh for the left wheel.                                                                                                                                                                                                                   |
| 24–28       | A **continuous joint** (unbounded rotation) connects the left wheel to the chassis. Line 25 positions the wheel 70 mm to the robot’s left. Line 28 declares the rotation axis along positive `y`.                                                                                           |
| 29–33       | `right_wheel_link` holds the visual and collision mesh for the right wheel.                                                                                                                                                                                                                 |
| 34–38       | A **continuous joint** connects the right wheel to the chassis. Line 35 positions the wheel 70 mm to the robot’s right.                                                                                                                                                                     |
| 39–43       | `computer_link` adds the onboard computer as a rigid body mounted on the chassis, using both visual and collision geometry.                                                                                                                                                                 |
| 44–47       | A **fixed joint** attaches the computer rigidly to `base_link`.                                                                                                                                                                                                                             |
| 48–52       | `camera_link` adds the camera mesh. The visual and collision geometry are both offset and slightly pitched downward to match the sensor’s mounting position.                                                                                                                                |
| 53–56       | A **fixed joint** attaches the camera to the chassis. Line 56 places the camera slightly forward and above the robot center with a small pitch angle.                                                                                                                                       |

> **Why no `<inertial>` elements yet?** For visualization alone they are optional. We add masses, inertias, and simulation-specific details later, once the robot’s geometry and kinematic tree are correct.

---

## 4 Installing Meshes and URDF Files

Open *`racademy_ws/src/racademy_description/CMakeLists.txt`* and add immediately after `find_package(ament_cmake REQUIRED)`:

```cmake
install(
  DIRECTORY meshes urdf
  DESTINATION share/${PROJECT_NAME}
)
```

This CMake rule copies both directories verbatim into `install/racademy_description/share/…` so that the `package://` URI resolves correctly at run‑time.

Re‑build and re‑source:

```bash
$ colcon build
$ source install/setup.bash
```

---

## 5 Visualising the Model in RViz

launch:

```bash
$ ros2 launch urdf_tutorial display.launch.py \
      model:=`pwd`/src/racademy_description/urdf/racademy.urdf.xacro
```

RViz should open with a green robot icon. Add a **RobotModel** display type if it is not present, and verify that the TF tree shows `base_footprint → base_link → wheel_right_link`.

---

## 6 Next Steps

- Add the left wheel and any caster wheels.
- Insert `<collision>` and `<inertial>` blocks for realistic physics.
- Create xacro *properties* for wheel radius, track width, and other parameters so you can tweak a single value and regenerate the whole model.

— **End of Chapter 2**
