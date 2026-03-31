# Chapter 6 – Bringing the Robot to Life in Gazebo (Ignition / Gazebo Sim)

> _Goal_: Spawn **racademy_ws** into the physics simulator, complete with realistic inertia, collision geometry, and friction coefficients—then bridge simulation time back to ROS 2.

## 1  Why Gazebo Ignition?

*Gazebo Ignition* (rebranded simply **Gazebo Sim** since 2023) is the next‑generation simulator for robots, offering modular rendering engines, advanced physics solvers, and a tight integration layer (`ros_gz_*` packages) for ROS 2. Compared with “Gazebo Classic,” Ignition uses a modern transport layer and C++17 codebase, while the ROS bridge automatically exposes everything as native ROS topics, services, and parameters.

Outcome of this chapter:

1. Add Gazebo‑specific tags without cluttering the visualization URDF.
2. Provide simplified collision shapes to speed up the solver.
3. Write a launch file that
   - converts Xacro → URDF,
   - publishes `/robot_description`,
   - sets *simulation time*,
   - spawns the robot into an **empty world**, and
   - starts the ROS↔Gazebo clock bridge.

## 2  Creating `racademy_ws_gazebo.xacro`

Place the file in *`racademy_ws_description/urdf/racademy_ws_gazebo.xacro`*.

```xml
<?xml version="1.0"?>                                   <!-- 1 -->
<robot name="racademy_ws" xmlns:xacro="http://ros.org/wiki/xacro"> <!-- 2 -->

  <!-- 3  High‑friction parameters for the drive wheels ▲ ▲ ▲ -->
  <gazebo reference="wheel_left_link">                   <!-- 3 -->
    <mu1>1e15</mu1>                                       <!-- 4 -->
    <mu2>1e15</mu2>                                       <!-- 5 -->
    <kp>1e12</kp>                                         <!-- 6 -->
    <kd>10</kd>                                           <!-- 7 -->
    <minDepth>0.001</minDepth>                            <!-- 8 -->
    <maxVel>0.1</maxVel>                                  <!-- 9 -->
    <fdir1>1 0 0</fdir1>                                  <!-- 10 -->
  </gazebo>

  <gazebo reference="wheel_right_link"> …same as above… </gazebo>

  <!-- 11  Lower friction on casters so they can swivel freely -->
  <gazebo reference="caster_front_link">                 <!-- 11 -->
    <mu1>0.1</mu1><mu2>0.1</mu2><kp>1e6</kp><kd>100</kd>
    <minDepth>0.001</minDepth><maxVel>1.0</maxVel>
  </gazebo>
  <gazebo reference="caster_rear_link"> …identical… </gazebo>
</robot>
```

| **Line(s)** | **Purpose**                                                                                                                                                                                                                                                                                                                                               |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1           | Standard XML header.                                                                                                                                                                                                                                                                                                                                      |
| 2           | Root element; we only store *Gazebo* extensions here.                                                                                                                                                                                                                                                                                                     |
| 3–10        | Wheel friction parameters. `mu1`/`mu2` are Coulomb friction coefficients in the two principal directions. They’re set absurdly high so the differential drive **bites** the ground during odometry tests. `kp`/`kd` form a contact"spring–damper" model to keep penetration minimal. `fdir1` forces the friction direction to align with the wheel tread. |
| 11–         | Casters get small friction so they don’t steer the robot.                                                                                                                                                                                                                                                                                                 |

## 3  Extending the Main URDF with Inertias, Collisions, and the Gazebo Include

Open *`racademy_ws_description/urdf/racademy_ws.urdf.xacro`* and add three key changes:

1. **Include the Gazebo fragment** right after the XML header:

   ```xml
   <xacro:include filename="$(find racademy_ws_description)/urdf/racademy_ws_gazebo.xacro"/>
   ```

2. **Inertial blocks** (`<inertial>`) for every link—taken from CAD or estimated via MeshLab.
3. **Collision geometry**: we reuse the full chassis STL, but **replace the wheel meshes with simple `<sphere>` shapes**(radius ≈ wheel radius) to cut collision computation time.

An excerpt for the right wheel (annotated):

```xml
<link name="wheel_right_link">
  <inertial> …mass & inertia matrix… </inertial>

  <visual>
    <origin xyz="0 0 0" rpy="1.57 0 0"/>
    <geometry><mesh filename="…/wheel_right_link.STL"/></geometry>
  </visual>

  <collision>                                          <!-- A -->
    <origin xyz="0 -0.015 0" rpy="1.57 0 0"/>       <!-- B -->
    <geometry><sphere radius="0.033"/></geometry>    <!-- C -->
  </collision>
</link>
```

| **A** | Collision tag used only by the physics engine. | | **B** | Slight offset so the sphere hugs the tread. | | **C** | A 33 mm sphere ≈ wheel radius → simulation stays fast.

Repeat for the left wheel and casters.

> **Hint** – If you later switch to *ODE* or *Bullet* inside Gazebo, primitive shapes dramatically improve contact stability over triangle meshes.

## 4  Creating `gazebo.launch.py`

Place the file in *`racademy_ws_description/launch/gazebo.launch.py`*.

```python
#!/usr/bin/env python3
"""Launch Gazebo Sim, spawn racademy_ws, bridge the clock, and use /use_sim_time."""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, ExecuteProcess
)
from launch.substitutions import Command, LaunchConfiguration, EnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    # Locate package share and its *parent* to expose meshes to Gazebo
    pkg_share = get_package_share_directory("racademy_ws_description")
    share_root = str(Path(pkg_share).parent)

    # ─────────────────── Launch Arguments ───────────────────
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(pkg_share, "urdf", "racademy_ws.urdf.xacro"),
        description="Absolute path to robot URDF/Xacro file",
    )

    # ─────────────────── Environment Variables ──────────────
    ign_resource = SetEnvironmentVariable(
        name="IGN_GAZEBO_RESOURCE_PATH",
        value=[share_root, ":", EnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", default_value="")],
    )
    gz_resource = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[share_root, ":", EnvironmentVariable("GZ_SIM_RESOURCE_PATH", default_value="")],
    )

    # Echo the result for debugging
    log_env = ExecuteProcess(
        cmd=["bash", "-lc", "echo IGN_GAZEBO_RESOURCE_PATH=$IGN_GAZEBO_RESOURCE_PATH"],
        output="screen",
    )

    # ─────────────────── Robot Description ──────────────────
    robot_description = ParameterValue(Command(["xacro ", LaunchConfiguration("model")]), value_type=str)

    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
    )

    # ─────────────────── Gazebo Server & Client ─────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch"), "/gz_sim.launch.py"
        ]),
        launch_arguments=[("gz_args", [" -v 4", " -r", " empty.sdf"])],
    )

    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description", "-name", "racademy_ws"],
    )

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
    )

    return LaunchDescription([
        log_env,
        model_arg,
        ign_resource,
        gz_resource,
        rsp_node,
        gazebo,
        spawn_entity,
        clock_bridge,
    ])
```

### 4.1  Major Sections Explained

| **Block**                        | **What it does**                                                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| _Environment Variables_          | Extend `IGN_GAZEBO_RESOURCE_PATH` and `GZ_SIM_RESOURCE_PATH` so Gazebo can locate your meshes **outside** its default install. |
| `robot_state_publisher`          | Publishes TF and `/robot_description`; `use_sim_time=True` tells rclpy to read the simulator clock.                            |
| `ros_gz_sim … /gz_sim.launch.py` | Starts the Ignition Gazebo server (`gz gui` if you add `-g` later) with an *empty world*.                                      |
| `ros_gz_sim create`              | Spawns the robot by subscribing to `/robot_description`.                                                                       |
| `ros_gz_bridge parameter_bridge` | Relays the `/clock` topic so all ROS nodes tick in sync.                                                                       |

## 5  Package Installation Updates

### 5.1  `CMakeLists.txt`

The rule added in Chapter 5 (`launch rviz`) already installs the *launch* directory, so no change is needed.

### 5.2  `package.xml`

Add simulator dependencies:

```xml
<exec_depend>ros_gz_sim</exec_depend>
<exec_depend>ros_gz_bridge</exec_depend>
```

(These pull in `gz-sim`, `gz-gui`, `ign-physics` libraries, etc.)

Re‑build and source:

```bash
$ colcon build --symlink-install
$ source install/setup.bash
```

> **Troubleshooting** – If the linker complains about *ignition‑math* versions, ensure you installed the matching `ros-humble-ros-gz-*` meta‑packages for your Ubuntu release.

## 6  Running the Simulator

```bash
$ ros2 launch racademy_ws_description gazebo.launch.py
```

- Gazebo GUI opens with an **empty plane**.
- The shell prints `SpawnEntity: Success` and places *racademy_ws* at (0,0,0).
- The clock bridge starts; verify with:
  ```bash
  $ ros2 topic echo /clock | head
  ```
- Inspect TF in RViz (fixed frame `base_footprint`).
- Drag wheel sliders (still running from Chapter 4) to see the robot roll.

---

## 7  Next Steps

- Add a **differential_drive_controller** via ROS 2 Control for velocity commands.
- Insert sensors (IMU, depth camera) and bridge their topics.
- Swap the ground plane for a realistic warehouse world.

— **End of Chapter 6**
