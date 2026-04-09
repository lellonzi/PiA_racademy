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