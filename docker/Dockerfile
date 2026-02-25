# Stage 1: Builder
FROM ros:humble AS builder

# Change to Tsinghua Mirror for apt to speed up build
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list \
    && sed -i 's@//security.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy main" > /etc/apt/sources.list.d/ros2-latest.list

ENV ROSDISTRO_INDEX_URL=https://mirrors.tuna.tsinghua.edu.cn/rosdistro/index-v4.yaml

WORKDIR /root/ws
COPY ros_ws/src ./src

# 🔴 关键修复：在安装 rosdep 之前或之后安装 pip3
RUN apt-get update && \
    apt-get install -y python3-pip \
    ros-humble-std-srvs \
    ros-humble-sensor-msgs \
    ros-humble-nav-msgs \
    ros-humble-geometry-msgs \
    && \
    . /opt/ros/humble/setup.bash && \
    colcon build --symlink-install

# Stage 2: Runtime (最小化运行环境)
FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive

# 安装运行时工具: rosbridge, nginx, curl, net-tools (用于测试)
RUN apt-get update && apt-get install -y \
    ros-humble-rosbridge-server \
    ros-humble-tf2-web-republisher \
    nginx \
    curl \
    net-tools \
    iputils-ping \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户 (安全最佳实践)
RUN useradd -m -u 1000 robotuser

# 复制构建产物
COPY --from=builder /root/ws/install /root/ws/install
COPY --from=builder /root/ws/src /root/ws/src

# 复制 Web 文件
COPY web/index.html /usr/share/nginx/html/index.html
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 复制测试文件 (可选，如果需要在容器内跑测试)
COPY tests /tests

# 权限设置
RUN chown -R robotuser:robotuser /root/ws /var/log/nginx /var/lib/nginx /usr/share/nginx/html

USER robotuser

EXPOSE 80 9090

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 健康检查：检查 Web 和 Rosbridge 端口
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:80 && netstat -tlnp | grep 9090 || exit 1

ENTRYPOINT ["/entrypoint.sh"]