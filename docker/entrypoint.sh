#!/bin/bash
set -e

# 加载 ROS 2 环境
source /opt/ros/humble/setup.bash
source /home/robotuser/ws/install/setup.bash

echo "🚀 Starting Cloud Robot System..."

# 1. Start Nginx
# 尝试启动 Nginx, 失败则回退到前台模式但作为一个后台任务运行
# 注意: robotuser 无 sudo 权限, 所以直接尝试 nginx
# 我们在 nginx.conf 中配置了 pid /tmp/nginx.pid 和 非root端口
nginx -g "daemon off;" &

# 2. Start Rosbridge
ros2 launch rosbridge_server rosbridge_websocket_launch.xml port:=9090 &

# 3. Wait for Rosbridge to be ready (optional)
sleep 2

# 4. Execute the CMD from Dockerfile (which runs the main launch file)
# This will keep the container running
echo "✅ System Ready. Visit http://localhost"
exec "$@"
