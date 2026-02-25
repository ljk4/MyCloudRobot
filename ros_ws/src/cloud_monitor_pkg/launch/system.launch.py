from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='cloud_monitor_pkg', executable='path_planner', name='path_planner'),
        Node(package='cloud_monitor_pkg', executable='param_service', name='param_service'),
    ])