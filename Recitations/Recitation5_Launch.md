# Chapter 5 – Automating Everything with a Launch File

> _Goal_: Start **robot_state_publisher**, **joint_state_publisher_gui**, and **RViz** with a *single* command, while keeping the URDF path configurable.

## 1 Why Launch Files?

A ROS 2 launch file is a Python script that describes **what** nodes to run, **how** to configure them, and **when** to start them. Launch files can also **include** other launch files, set environment variables, and declare user‑tunable arguments—all while remaining platform‑agnostic.

Key advantages:

- One‑line startup for complex systems
- Central place to document default parameters and topic remappings
- Shareable across team members without exposing absolute paths

Launch files live in a package’s *`launch/`* directory and traditionally end in `.launch.py`.

---

## 2 Writing `display.launch.py`

Create *`racademy_ws/src/racademy_description/launch/display.launch.py`* and paste the code below. As usual, every line is annotated.

```python
#!/usr/bin/env python3
"""Launch RViz with the robot model and GUI sliders ready to go."""

# 1  Standard libraries
import os

# 2  ament_index lets us resolve package directories at run‑time
from ament_index_python.packages import get_package_share_directory

# 3  Core launch classes
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration

# 4  ROS‑specific launch helpers
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    """Compose and return a LaunchDescription object."""

    # 5  Locate the racademy_description package regardless of workspace path
    racademy_description_dir = get_package_share_directory("racademy_description")

    # 6  User‑configurable argument: path to the URDF/Xacro
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(
            racademy_description_dir, "urdf", "racademy.urdf.xacro"
        ),
        description="Absolute path to robot URDF or Xacro file",
    )

    # 7  Expand xacro *at launch time* and expose as a parameter value
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]),
        value_type=str,
    )

    # 8  robot_state_publisher node with the generated URDF injected
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )

    # 9  GUI sliders for joint positions
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
    )

    # 10  RViz pre‑loaded with our saved layout
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(racademy_description_dir, "rviz", "display.rviz")],
    )

    # 11  Assemble all actions into a LaunchDescription
    return LaunchDescription([
        model_arg,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node,
    ])
```

### 2.1 Explanation Table

| **Line(s)** | **Purpose**                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------ |
| 1–4         | Imports from the Python standard library and the ROS 2 launch API.                                                 |
| 5           | `get_package_share_directory()` finds the *installed* location of any package.                                     |
| 6           | Declares a launch‑time argument `model` so users can override the URDF path.                                       |
| 7           | Uses the `xacro` CLI to convert the file into pure URDF; the result is mapped to the `robot_description`parameter. |
| 8           | Starts `robot_state_publisher` with that parameter.                                                                |
| 9           | Starts the joint‑slider GUI.                                                                                       |
| 10          | Launches RViz and loads the layout we saved in Chapter 4.                                                          |
| 11          | Returns a list of launch actions as the `LaunchDescription`.                                                       |

---

## 3 Installing Launch and RViz Assets

### 3.1 Amend *`CMakeLists.txt`*

Add `launch` and `rviz` to the install rule (after the previous chapters):

```cmake
install(
  DIRECTORY meshes urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
)
```

### 3.2 Extend *`package.xml`*

Insert these runtime dependencies **after** `<buildtool_depend>`:

```xml
<exec_depend>robot_state_publisher</exec_depend>
<exec_depend>joint_state_publisher_gui</exec_depend>
<exec_depend>rviz2</exec_depend>
<exec_depend>ros2launch</exec_depend>
```

> **Note** – You do *not* need to add `xacro`; it is part of `ros-humble-xacro`, already required by `robot_state_publisher`.

Re‑build and re‑source:

```bash
$ colcon build --symlink-install
$ source install/setup.bash
```

---

## 4 Using the Launch File

Start the entire visualization stack with a single command:

```bash
$ ros2 launch racademy_description display.launch.py
```

Pass a custom robot model if desired:

```bash
$ ros2 launch racademy_description display.launch.py \
      model:=/path/to/alternative_robot.urdf.xacro
```

You should see:

1. **Terminal output** from all three nodes.
2. **RViz** showing the robot model.
3. **Joint State GUI** for wheel sliders.

---

— **End of Chapter 5**

---
