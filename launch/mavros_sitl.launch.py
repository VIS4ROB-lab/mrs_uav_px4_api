#!/usr/bin/env python3
"""
MAVROS launch file for PX4 SITL (Software-In-The-Loop) simulation.

This launch file configures MAVROS to connect to PX4 SITL via UDP,
unlike the hardware version which uses serial ports.
"""

import launch
import os
import launch_ros

from launch_ros.actions import Node, SetParameter
from launch.actions import GroupAction, IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import (
    LaunchConfiguration,
    IfElseSubstitution,
    PythonExpression,
    PathJoinSubstitution,
    EnvironmentVariable,
)
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    """Generate launch description for MAVROS with PX4 SITL."""

    ld = launch.LaunchDescription()

    pkg_name = "mrs_uav_px4_api"
    this_pkg_path = get_package_share_directory(pkg_name)

    # Arguments from environment
    uav_name = os.getenv("UAV_NAME", "uav1")
    uav_id = os.getenv("UAV_ID", "1")
    use_sim_time = os.getenv('USE_SIM_TIME', "true") == "true"
    respawn_mavros = os.getenv('respawn_mavros', "true") == "true"

    # SITL-specific: UDP connection to localhost on port 14540
    # PX4 SITL opens UDP port 14540 by default, listening for ground stations
    fcu_url = "udp://127.0.0.1:14540@127.0.0.1:14550"
    gcs_url = "tcp-l://"

    tgt_system = int(uav_id)
    namespace = uav_name

    px4_launch_arguments = {
        "fcu_url": fcu_url,
        "gcs_url": gcs_url,
        "tgt_system": str(tgt_system),
        "tgt_component": str(1),
        "log_output": "screen",
        "fcu_protocol": "v2.0",
        "respawn_mavros": str(respawn_mavros),
        "namespace": uav_name + "/mavros",
        "pluginlists_yaml": this_pkg_path + "/config/mavros_plugins.yaml",
        "config_yaml": this_pkg_path + "/config/mavros_px4_config.yaml",
        "use_sim_time": str(use_sim_time),
    }

    print(f"[MAVROS SITL] Connecting to PX4 SITL at {fcu_url}")
    print(f"[MAVROS SITL] UAV Name: {uav_name}, UAV ID: {uav_id}, Use Sim Time: {use_sim_time}")

    ld.add_action(
        IncludeLaunchDescription(
            XMLLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('mrs_uav_px4_api'),
                    'launch/mavros.launch')
                ),
                launch_arguments=px4_launch_arguments.items()
        )
    )

    # Static transform from FCU to Garmin frame
    ld.add_action(
        launch_ros.actions.Node(
            package='tf2_ros',
            namespace='',
            executable='static_transform_publisher',
            name='fcu_to_garmin',
            arguments=[
                "0.0", "0.0", "-0.05",
                "0", "1.57", "0",
                uav_name + "/fcu",
                uav_name + "/garmin"
            ],
        )
    )

    return ld
