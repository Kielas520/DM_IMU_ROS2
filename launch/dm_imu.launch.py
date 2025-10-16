from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('port', default_value='/dev/ttyACM0'),
        DeclareLaunchArgument('baudrate', default_value='921600'),
        DeclareLaunchArgument('frame_id', default_value='imu_link'),
        DeclareLaunchArgument('publish_rpy', default_value='true'),
        DeclareLaunchArgument('qos_reliable', default_value='true'),
        DeclareLaunchArgument('verbose', default_value='true'),

        Node(
            package='dm_imu',
            executable='dm_imu_node',
            name='dm_imu',
            output='screen',
            parameters=[{
                'port': LaunchConfiguration('port'),
                'baudrate': LaunchConfiguration('baudrate'),
                'frame_id': LaunchConfiguration('frame_id'),
                'publish_rpy': LaunchConfiguration('publish_rpy'),
                'qos_reliable': LaunchConfiguration('qos_reliable'),
                'verbose': LaunchConfiguration('verbose'),
            }]
        )
    ])
