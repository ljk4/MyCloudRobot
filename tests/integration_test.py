#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROS 2 集成测试脚本
用于验证 param_service_node 的逻辑是否正确响应服务调用。
可以在 CI 管道中运行，也可以本地运行。
"""
import pytest
import rclpy
from std_srvs.srv import SetBool, Trigger
from rclpy.node import Node
import time

class TestClient(Node):
    def __init__(self):
        super().__init__('integration_test_client')

@pytest.fixture(scope="module")
def ros_context():
    """初始化 ROS 2 上下文"""
    rclpy.init()
    yield
    rclpy.shutdown()

def test_safety_mode_service(ros_context):
    """测试 1: 切换安全模式"""
    node = TestClient()
    client = node.create_client(SetBool, 'set_safety_mode')
    
    # 等待服务可用 (最多等 5 秒)
    if not client.wait_for_service(timeout_sec=5.0):
        raise RuntimeError("服务 /set_safety_mode 未找到！节点可能未启动。")

    # 请求开启安全模式 (True)
    req = SetBool.Request()
    req.data = True
    future = client.call_async(req)
    
    # 简单的事件循环等待结果 (在测试脚本中简化处理)
    while rclpy.ok() and not future.done():
        rclpy.spin_once(node, timeout_sec=0.1)
    
    if future.exception():
        raise Exception(f"服务调用失败: {future.exception()}")
    
    response = future.result()
    assert response.success is True, "服务返回成功标志应为 True"
    assert "SAFE" in response.message, "返回消息应包含 SAFE 字样"
    
    node.get_logger().info(f"✅ 测试通过: {response.message}")
    
    # 清理
    node.destroy_node()

def test_reset_service(ros_context):
    """测试 2: 重置机器人参数"""
    node = TestClient()
    client = node.create_client(Trigger, 'reset_robot')
    
    if not client.wait_for_service(timeout_sec=5.0):
        raise RuntimeError("服务 /reset_robot 未找到！")

    req = Trigger.Request()
    future = client.call_async(req)
    
    while rclpy.ok() and not future.done():
        rclpy.spin_once(node, timeout_sec=0.1)
        
    if future.exception():
        raise Exception(f"服务调用失败: {future.exception()}")
    
    response = future.result()
    assert response.success is True, "重置服务应成功"
    assert "Reset" in response.message, "返回消息应包含 Reset 字样"
    
    node.get_logger().info(f"✅ 测试通过: {response.message}")
    node.destroy_node()

if __name__ == '__main__':
    # 允许直接运行 python integration_test.py
    pytest.main([__file__, "-v"])