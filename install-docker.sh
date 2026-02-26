#!/bin/bash
################################################################################
# Docker 自动化安装脚本 (适用于 Ubuntu 20.04/22.04/24.04)
# 使用阿里云镜像源，解决国内网络问题
# 创建时间: 2026-02-24
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查是否以 root 运行
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 sudo 运行此脚本: sudo $0"
        exit 1
    fi
}

# 检查系统
check_system() {
    if [ ! -f /etc/os-release ]; then
        log_error "无法识别操作系统"
        exit 1
    fi
    source /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        log_warn "此脚本主要针对 Ubuntu/Debian，当前系统: $ID"
    fi
    log_info "检测到系统: $PRETTY_NAME"
}

# 清理旧版本 Docker
cleanup_old_docker() {
    log_info "清理旧版本 Docker..."
    apt remove docker docker-engine docker.io containerd runc -y 2>/dev/null || true
    apt autoremove -y 2>/dev/null || true
    log_success "清理完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖包..."
    apt update
    apt install -y ca-certificates curl gnupg lsb-release apt-transport-https
    log_success "依赖安装完成"
}

# 添加 Docker GPG 密钥
add_docker_gpg() {
    log_info "添加 Docker GPG 密钥..."
    install -m 0755 -d /etc/apt/keyrings
    
    # 尝试多个镜像源
    MIRRORS=(
        "https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg"
        "https://mirrors.cloud.tencent.com/docker-ce/linux/ubuntu/gpg"
        "https://download.docker.com/linux/ubuntu/gpg"
    )
    
    for mirror in "${MIRRORS[@]}"; do
        log_info "尝试镜像: $mirror"
        if curl -fsSL --connect-timeout 10 "$mirror" | gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null; then
            log_success "GPG 密钥添加成功 (使用: $mirror)"
            chmod a+r /etc/apt/keyrings/docker.gpg
            return 0
        fi
    done
    
    log_error "所有镜像源都失败，请检查网络连接"
    exit 1
}

# 添加 Docker 仓库
add_docker_repo() {
    log_info "添加 Docker 仓库..."
    
    CODENAME=$(lsb_release -cs)
    
    # 使用阿里云镜像源
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $CODENAME stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    log_success "Docker 仓库添加完成"
}

# 安装 Docker
install_docker() {
    log_info "安装 Docker..."
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    log_success "Docker 安装完成"
}

# 配置 Docker 服务
configure_docker() {
    log_info "配置 Docker 服务..."
    
    # 启动并设置开机自启
    systemctl enable docker
    systemctl start docker
    systemctl status docker --no-pager
    
    log_success "Docker 服务已启动"
}

# 配置镜像加速器
configure_mirror() {
    log_info "配置 Docker 镜像加速器..."
    
    mkdir -p /etc/docker
    
    cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://dhub.kubesre.xyz"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF
    
    systemctl daemon-reload
    systemctl restart docker
    
    log_success "镜像加速器配置完成"
}

# 配置非 root 用户
configure_user() {
    log_info "配置非 root 用户使用 Docker..."
    
    # 获取当前登录用户（排除 root）
    if [ -n "$SUDO_USER" ]; then
        USERNAME=$SUDO_USER
    else
        USERNAME=$(whoami)
    fi
    
    if [ "$USERNAME" != "root" ]; then
        usermod -aG docker $USERNAME
        log_success "用户 $USERNAME 已加入 docker 组"
        log_warn "请执行 'newgrp docker' 或重新登录使组变更生效"
    else
        log_warn "当前以 root 运行，跳过用户配置"
    fi
}

# 验证安装
verify_installation() {
    log_info "验证 Docker 安装..."
    
    echo ""
    echo "========================================"
    docker --version
    docker compose version
    echo "========================================"
    
    # 测试运行 hello-world
    log_info "测试运行 hello-world 容器..."
    if docker run --rm hello-world 2>/dev/null; then
        log_success "Docker 安装验证成功！"
    else
        log_warn "hello-world 测试失败，但 Docker 可能仍可正常使用"
    fi
    
    echo ""
    log_info "Docker 信息:"
    docker info --format '{{.ServerVersion}}' 2>/dev/null || echo "无法获取详细信息"
}

# 主函数
main() {
    echo ""
    echo "========================================"
    echo "  🐳 Docker 自动化安装脚本"
    echo "  适用于 Ubuntu/Debian"
    echo "========================================"
    echo ""
    
    check_root
    check_system
    cleanup_old_docker
    install_dependencies
    add_docker_gpg
    add_docker_repo
    install_docker
    configure_docker
    configure_mirror
    configure_user
    verify_installation
    
    echo ""
    echo "========================================"
    echo "  ✅ Docker 安装完成！"
    echo "========================================"
    echo ""
    echo "常用命令:"
    echo "  docker --version          # 查看版本"
    echo "  docker ps                 # 查看运行中的容器"
    echo "  docker images             # 查看镜像"
    echo "  docker compose up -d      # 启动容器"
    echo ""
    echo "如果非 root 用户使用 docker，请执行:"
    echo "  newgrp docker"
    echo ""
}

# 执行主函数
main "$@"