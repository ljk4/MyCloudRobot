# CI/CD 构建与测试问题排查记录

## 问题一：ROS 2 节点启动失败 (No executable found)

### 现象
CI 流程中执行 `source install/setup.bash` 后，运行 `rocket param_service node...` 时报错：
```
Run source /opt/ros/humble/setup.bash
🚀 Starting param_service node...
No executable found
❌ Error: Node param_service_node did not start!
```

### 原因
setup.py 中的 `entry_points` 定义了控制台脚本，但 `colcon build --symlink-install` 在处理 Python 包时，有时不会自动将脚本链接到 ROS 2 预期的 `lib/package_name` 目录下，特别是当 `zip_safe=True` 时，或者缺少明确的安装配置时。

### 解决方法
1.  **添加 `setup.cfg` 配置**：
    在包根目录下创建 `setup.cfg` 文件，显式指定脚本安装路径：
    ```ini
    [develop]
    script_dir=$base/lib/cloud_monitor_pkg
    [install]
    install_scripts=$base/lib/cloud_monitor_pkg
    ```
    这确保了可执行文件会被放置在 `install/cloud_monitor_pkg/lib/cloud_monitor_pkg/` 下，这也是 `ros2 run` 寻找可执行文件的地方。

2.  **修改 `setup.py`**：
    将 `zip_safe=True` 改为 `False`。
    ```python
    setup(
        ...
        zip_safe=False,
        ...
    )
    ```

## 问题二：集成测试文件未找到 (No such file or directory)

### 现象
CI 流程在运行集成测试时报错：
```
python3: can't open file '/__w/MyCloudRobot/MyCloudRobot/tests/integration_test.py': [Errno 2] No such file or directory
```

### 原因
文件名中包含了多余的空格。通过 `ls -la tests/` 查看到文件名为 `' integration_test.py'` (注意开头的空格)。这可能是由于之前的操作误命名导致的。

### 解决方法
重命名文件，移除开头的空格：
```bash
git mv "tests/ integration_test.py" tests/integration_test.py
```

## 问题三：Docker 构建网络超时

### 现象
在 Docker 容器中运行 `rosdep update` 或安装依赖时，由于网络问题导致连接 GitHub 或 rosdep 源失败：
```
<urlopen error _ssl.c:990: The handshake operation timed out>
```

### 解决方法
在 `Dockerfile` 中设置环境变量，使用清华大学的 ROSDistro 镜像源：
```dockerfile
ENV ROSDISTRO_INDEX_URL=https://mirrors.tuna.tsinghua.edu.cn/rosdistro/index-v4.yaml
```
这显著提高了国内环境下构建的稳定性和速度。
