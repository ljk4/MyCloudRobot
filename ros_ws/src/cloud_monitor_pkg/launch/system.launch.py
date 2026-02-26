from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='cloud_monitor_pkg', executable='path_planner', name='path_planner'),
        Node(package='rosbridge_server', executable='rosbridge_websocket', name='rosbridge_websocket'),
    ])