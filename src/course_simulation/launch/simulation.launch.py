"""Start one Gazebo server, one bridge, the PR06 description and two adapters."""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def launch_nodes(context):
    share = Path(get_package_share_directory('course_simulation'))
    description_share = Path(get_package_share_directory('course_description'))
    namespace = LaunchConfiguration('namespace').perform(context)
    world = LaunchConfiguration('world').perform(context)
    bridge_config = LaunchConfiguration('bridge_config').perform(context)
    headless = LaunchConfiguration('headless').perform(context).lower() == 'true'
    resource_path = str(share / 'models')
    existing = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    if existing:
        resource_path += os.pathsep + existing
    arguments = ['gz', 'sim', '-r']
    if headless:
        arguments += ['-s', '--headless-rendering']
    arguments.append(world)
    description = xacro.process_file(
        str(description_share / 'urdf' / 'vehicle.urdf.xacro')).toxml()
    return [
        ExecuteProcess(
            cmd=arguments, output='screen',
            additional_env={'GZ_SIM_RESOURCE_PATH': resource_path}),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            namespace=namespace, output='screen',
            parameters=[{'robot_description': description, 'use_sim_time': True}],
            remappings=[('tf', '/tf'), ('tf_static', '/tf_static')]),
        Node(
            package='ros_gz_bridge', executable='parameter_bridge', name='bridge',
            namespace=namespace, output='screen',
            parameters=[{'config_file': bridge_config, 'use_sim_time': True}]),
        Node(
            package='course_simulation', executable='drive_adapter',
            namespace=namespace, output='screen', parameters=[{'use_sim_time': True}]),
        Node(
            package='course_simulation', executable='odom_adapter',
            namespace=namespace, output='screen', parameters=[{'use_sim_time': True}]),
    ]


def generate_launch_description():
    share = Path(get_package_share_directory('course_simulation'))
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=str(share / 'worlds/mcity-minimal.sdf')),
        DeclareLaunchArgument('bridge_config', default_value=str(share / 'config/bridge.yaml')),
        DeclareLaunchArgument('headless', default_value='true'),
        DeclareLaunchArgument('namespace', default_value='simulation'),
        OpaqueFunction(function=launch_nodes),
    ])
