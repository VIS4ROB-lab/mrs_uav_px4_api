#!/usr/bin/env python3

import launch
import os
import launch_ros

from launch_ros.actions import Node, SetParameter
from launch.actions import GroupAction, IncludeLaunchDescription, DeclareLaunchArgument

from launch_xml.launch_description_sources import XMLLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    ld = launch.LaunchDescription()

    pkg_name = "mrs_uav_px4_api"
    this_pkg_path = get_package_share_directory(pkg_name)

    uav_name = os.getenv("UAV_NAME", "uav")
    uav_id = os.getenv("UAV_ID", "1")
    use_sim_time=os.getenv('USE_SIM_TIME', "false") == "true"
    respawn_mavros=os.getenv('respawn_mavros', "false") == "true"

    fcu_url = "/dev/pixhawk:2000000"
    gcs_url = "tcp-l://"

    tgt_system = int(uav_id)
    px4_launch_arguments = {
        "fcu_url": fcu_url,
        "gcs_url": gcs_url,
        "tgt_system": str(tgt_system),
        "tgt_component": str(1),
        "log_output": "screen",
        "fcu_protocol": "v2.0",
        "respawn_mavros": str(respawn_mavros),
        "namespace": uav_name + "/mavros",
        "pluginlists_yaml":  this_pkg_path + "/config/mavros_plugins.yaml",
        "config_yaml": this_pkg_path + "/config/mavros_px4_config.yaml",
        "base_link_frame_id": uav_name + "/base_link",
        "odom_frame_id": uav_name + "/odom",
        "map_frame_id": uav_name + "/map",
    }

    print(f"[MAVROS REAL] Connecting to PX4 REAL at {fcu_url}")
    print(f"[MAVROS REAL] UAV Name: {uav_name}, UAV ID: {uav_id}, Use Sim Time: {use_sim_time}")

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

    return ld


