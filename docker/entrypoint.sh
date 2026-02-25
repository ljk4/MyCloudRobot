#!/bin/bash
set -e

# 加载 ROS 2 环境
source /opt/ros/humble/setup.bash
source /home/robotuser/ws/install/setup.bash

echo "🚀 Starting Cloud Robot System..."

# 1. Start Nginx (作为普通用户可能需要特殊配置，这里简化为后台运行)
# 如果报错权限，可在 Dockerfile 中修改 nginx.conf 的 user 或 pid 路径
sudo service nginx start 2>/dev/null || nginx -g "daemon off;" &

# 2. Start Rosbridge
ros2 launch rosbridge_server rosbridge_websocket_launch.xml port:=9090 &

# 3. Start TF Republisher
ros2 run tf2_web_republisher tf2_web_republisher &

# 4. Start Custom Nodes
ros2 run cloud_monitor_pkg simulator &
ros2 run cloud_monitor_pkg param_service &

echo "✅ System Ready. Visit http://localhost"

# 保持容器运行
wait