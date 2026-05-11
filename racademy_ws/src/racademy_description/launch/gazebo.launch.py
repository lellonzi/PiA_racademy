#!/usr/bin/env python3
"""Launch Gazebo Sim, spawn racademy_ws, bridge the clock, and use /use_sim_time."""

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