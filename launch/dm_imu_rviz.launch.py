import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 尝试加载包内 rviz/imu.rviz；若不存在，就起空白 RViz
    try:
        pkg_share = get_package_share_directory('dm_imu')
        default_rviz = os.path.join(pkg_share, 'rviz', 'imu.rviz')
    except Exception:
        default_rviz = ''

    return LaunchDescription([
        DeclareLaunchArgument('port', default_value='/dev/ttyACM0'),
        DeclareLaunchArgument('baudrate', default_value='921600'),
        DeclareLaunchArgument('frame_id', default_value='imu_link'),
        DeclareLaunchArgument('publish_rpy', default_value='true'),
        DeclareLaunchArgument('qos_reliable', default_value='true'),
        DeclareLaunchArgument('verbose', default_value='true'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz),

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
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', LaunchConfiguration('rviz_config')],
        ),
    ])
