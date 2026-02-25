# Stage 1: Builder (使用预构建的基础镜像，包含编译工具和依赖)
# ARG DOCKER_USER
ARG DOCKER_USER=liujiankang123
FROM ${DOCKER_USER}/cloud-robot-viz-base:latest AS builder


SHELL ["/bin/bash", "-c"]

# 基础镜像已经创建了 /ws 目录并作为 WORKDIR 防止权限问题
# 但为了保险起见，显式声明工作目录
WORKDIR /home/robotuser/ws

# 优化构建缓存：
# 基础镜像已经包含了所有 ros-* 的依赖。
# 我们只需要复制源代码。
COPY --chown=robotuser:robotuser ros_ws/src ./src

# 编译 ROS 工作空间
# 使用 source 加载环境，因为基础镜像已经安装了 ROS
RUN source /opt/ros/humble/setup.bash && \
    colcon build  --cmake-args -DCMAKE_BUILD_TYPE=Release

# Stage 2: Runtime
# 直接使用包含运行时环境（nginx, rosbridge等）的基础镜像
ARG DOCKER_USER=liujiankang123
FROM ${DOCKER_USER}/cloud-robot-viz-base:latest

ENV DEBIAN_FRONTEND=noninteractive

# 创建并设置工作目录
WORKDIR /home/robotuser/ws

# 从 Builder 阶段复制编译产物 (install, build, log)
# 注意：我们要把文件所有权给 robotuser
COPY --from=builder --chown=robotuser:robotuser /home/robotuser/ws/install ./install
COPY --from=builder --chown=robotuser:robotuser /home/robotuser/ws/build ./build
COPY --from=builder --chown=robotuser:robotuser /home/robotuser/ws/log ./log

# 复制配置文件
# 假设 entrypoint.sh 和 nginx.conf 在 docker/ 目录下
COPY --chown=robotuser:robotuser docker/entrypoint.sh /entrypoint.sh
COPY --chown=robotuser:robotuser docker/nginx.conf /etc/nginx/nginx.conf
COPY --chown=robotuser:robotuser web /home/robotuser/web

# 设置脚本权限
# 由于我们是用 root 用户 copy 进去的 (Docker默认行为)，但在 COPY 时加了 chown
# 我们只需要确保 entrypoint 可执行
USER root
RUN chmod +x /entrypoint.sh && \
    # 确保 nginx 可以在非 root 下读取配置和 web 目录
    # (nginx.conf 需要配置 user robotuser; 或者运行在非特权端口)
    chmod -R 755 /home/robotuser/web

# 切换回非 root 用户运行应用
USER robotuser

# 暴露端口 (8080: Nginx, 9090: Rosbridge)
EXPOSE 8080 9090

# 设置入口点
ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "cloud_monitor_pkg", "system.launch.py"]
