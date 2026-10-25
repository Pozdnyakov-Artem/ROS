from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


def launch_nodes(context):
    share = Path(get_package_share_directory('course_description'))
    model = LaunchConfiguration('model').perform(context)
    description = xacro.process_file(model).toxml()
    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': ParameterValue(description, value_type=str),
                'use_sim_time': False,
            }],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', str(share / 'rviz' / 'model.rviz')],
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),
    ]


def generate_launch_description():
    share = Path(get_package_share_directory('course_description'))
    return LaunchDescription([
        DeclareLaunchArgument(
            'model', default_value=str(share / 'urdf' / 'vehicle.urdf.xacro'),
        ),
        DeclareLaunchArgument('rviz', default_value='true'),
        OpaqueFunction(function=launch_nodes),
    ])
