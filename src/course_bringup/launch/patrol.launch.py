from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('record', default_value='false'),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag'),
        DeclareLaunchArgument(
            'subscriber_reliability',
            default_value='reliable',
            choices=['reliable', 'best_effort'],
        ),
        LogInfo(msg=[
            'namespace=', namespace,
            ' subscriber_reliability=', subscriber_reliability,
            ' record=', record,
        ]),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            namespace='/',
            output='screen',
        ),
        Node(
            package='patrol',
            executable='patrol',
            namespace=namespace,
            remappings=[
                ('turtle1/pose', '/turtle1/pose'),
                ('cmd_vel', '/turtle1/cmd_vel'),
            ],
            output='screen',
        ),
        Node(
            package='patrol',
            executable='pose_relay',
            namespace=namespace,
            remappings=[('pose', '/turtle1/pose')],
            output='screen',
        ),
        Node(
            package='patrol',
            executable='pose_subscriber',
            namespace=namespace,
            parameters=[{'reliability': subscriber_reliability}],
            output='screen',
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-s', 'mcap',
                '-o', bag_dir,
                '--topics', ['/', namespace, '/sensor_pose'],
            ],
            condition=IfCondition(record),
            output='screen',
        ),
    ])
