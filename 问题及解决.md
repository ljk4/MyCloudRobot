# CI/CD 构建与测试问题排查记录

## 1. ROS 2 节点启动失败 (No executable found)

### 现象
CI 流程中执行 `ros2 run cloud_monitor_pkg param_service` 时报错：
```
No executable found
❌ Error: Node param_service_node did not start!
```

### 原因
ROS 2 的 Python 包在使用 `colcon build --symlink-install` 时，需要明确指定脚本安装路径，否则 `ros2 run` 无法在预期位置（`lib/package_name`）找到可执行文件。`setup.py` 中 `zip_safe=True` 也会影响资源加载。

### 解决方法
1.  **添加 `setup.cfg` 配置**：
    在包根目录创建 `setup.cfg`，强制指定脚本安装到 `lib` 目录：
    ```ini
    [develop]
    script_dir=$base/lib/cloud_monitor_pkg
    [install]
    install_scripts=$base/lib/cloud_monitor_pkg
    ```
2.  **修改 `setup.py`**：将 `zip_safe=True` 改为 `False`。

## 2. Docker 构建错误 (GPG key error & Permission denied)

### 问题 A: GPG 签名错误
**现象**: `apt-get update` 报错 `The following signatures couldn't be verified... NO_PUBKEY ...`。
**原因**: Dockerfile 中强行覆盖了 ROS 2 的 apt 源为清华源，但未导入对应的 GPG 公钥，或者基础镜像内的密钥与镜像源不匹配。
**解决**: 仅替换 Ubuntu 系统源（`archive.ubuntu.com` -> `mirrors.tuna.tsinghua.edu.cn`），**保留** ROS 2 官方源配置（不修改 `/etc/apt/sources.list.d/ros2-latest.list`）。

### 问题 B: 权限不足
**现象**: `chmod: changing permissions of '/entrypoint.sh': Operation not permitted`
**原因**: Dockerfile 中先切换了 `USER robotuser`，然后再复制和修改 root 拥有的 `/entrypoint.sh`。
**解决**:
1.  调整指令顺序：先 `COPY` 和 `chmod`，最后再切换 `USER`。
2.  使用 `COPY --chown=robotuser:robotuser` 确保文件归属正确。

### 问题 C: Shell 兼容性
**现象**: `source: not found` 或 `Bad substitution`。
**原因**: Docker 默认使用 `/bin/sh`，不支持 `source` 命令（bash 特有）。
**解决**: 在 Dockerfile 头部添加 `SHELL ["/bin/bash", "-c"]`。

## 3. 部署时 SSH 认证失败

### 现象
CD 流程报错：`ssh: handshake failed: ssh: unable to authenticate, attempted methods [none publickey]`

### 原因
服务器上的 `~/.ssh/authorized_keys` 文件为空，或者 GitHub Secrets 中的 `SSH_KEY` 与服务器公钥不匹配。

### 解决
1.  生成新的密钥对（如果需要）。
2.  将公钥内容追加到服务器的授权列表：`cat id_ed25519.pub >> ~/.ssh/authorized_keys`。
3.  将私钥内容更新到 GitHub Repository Secrets (`SSH_KEY`)。

---

## 4. 集成测试文件命名错误
**现象**: `python3: can't open file ...: [Errno 2] No such file`
**原因**: 文件名开头包含意外的空格（`' integration_test.py'`）。
**解决**: 重命名文件 `git mv "tests/ integration_test.py" tests/integration_test.py`。
