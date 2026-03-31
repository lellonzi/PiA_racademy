# URDF Tutorials for ROS 2

**Unified Robot Description Format (URDF)** is the standard XML-based file format used in ROS 2 to describe the physical structure, kinematics, and appearance of a robot. These tutorials follow the official ROS 2 Humble documentation and show how to embed URDF files into a proper ROS 2 workspace.

## Prerequisites

- ROS 2 Humble installed
- Basic understanding of ROS 2 concepts (nodes, topics, packages)
- Familiarity with XML syntax

## Tutorial Series

| # | Tutorial | Description |
|---|----------|-------------|
| 01 | [Introduction to URDF](01_introduction.md) | URDF structure, XML elements, and ROS 2 integration |
| 02 | [Building a Visual Robot Model](02_visual_robot_model.md) | Links, joints, materials, and mesh files |
| 03 | [Movable Joints](03_movable_joints.md) | Continuous, revolute, and prismatic joints |
| 04 | [Physical and Collision Properties](04_physical_properties.md) | Inertia, mass, collision geometry |
| 05 | [Using Xacro](05_xacro.md) | Macros, constants, and math for cleaner URDF |
| 06 | [Robot State Publisher](06_robot_state_publisher.md) | Publishing TF transforms from URDF |
| 07 | [Gazebo Simulation](07_gazebo_simulation.md) | Simulating robots with ros2_control and Gazebo |
| 08 | [Exporting URDF from CAD](08_exporting_urdf.md) | Tools for generating URDF from CAD software |

## Workspace Layout Reference

Every URDF-based robot follows this package structure inside a ROS 2 workspace:

```
my_robot_ws/
└── src/
    └── my_robot_description/
        ├── urdf/
        │   ├── my_robot.urdf.xacro          # Main robot definition
        │   ├── my_robot_gazebo.xacro        # Gazebo plugins
        │   └── my_robot_ros2_control.xacro  # ros2_control hardware interface
        ├── meshes/
        │   ├── base_link.STL
        │   └── wheel.STL
        ├── launch/
        │   ├── display.launch.py            # RViz visualization
        │   └── gazebo.launch.py             # Gazebo simulation
        ├── rviz/
        │   └── my_robot.rviz
        ├── package.xml
        └── CMakeLists.txt
```

## Quick Start

```bash
# Install tutorial dependencies
sudo apt install ros-humble-urdf-tutorial
sudo apt install ros-humble-joint-state-publisher-gui
sudo apt install ros-humble-robot-state-publisher
sudo apt install ros-humble-xacro

# Verify URDF file syntax
check_urdf my_robot.urdf

# Convert Xacro to URDF
xacro my_robot.urdf.xacro > my_robot.urdf

# Launch robot visualization in RViz
ros2 launch urdf_tutorial display.launch.py model:=my_robot.urdf
```

## Key Tools

| Tool | Purpose |
|------|---------|
| `check_urdf` | Validate URDF syntax and report link/joint tree |
| `xacro` | Process Xacro macros and generate URDF |
| `joint_state_publisher_gui` | GUI sliders to manually set joint positions |
| `robot_state_publisher` | Publishes TF transforms from URDF + joint states |
| `rviz2` | 3D visualization of the robot model |

## References

- [Official ROS 2 URDF Tutorials](https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/URDF-Main.html)
- [URDF XML Specification](http://wiki.ros.org/urdf/XML)
- [Xacro Documentation](http://wiki.ros.org/xacro)
