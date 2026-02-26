#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROS 2 集成测试脚本
用于验证 PathPlannerNode 的寻路逻辑是否正确响应。
"""
import pytest
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time
import threading

class PathPlannerTester(Node):
    def __init__(self):
        super().__init__('integration_test_client')
        self.publisher_ = self.create_publisher(String, 'game_request', 10)
        self.subscription = self.create_subscription(
            String,
            'game_response',
            self.listener_callback,
            10)
        self.received_response = None
        self.get_logger().info("🧪 Test Client Ready")

    def listener_callback(self, msg):
        self.get_logger().info(f"📩 Received response: {msg.data}")
        self.received_response = json.loads(msg.data)

    def send_request(self, start, goal, obstacles):
        request_data = {
            "start": start,
            "goal": goal,
            "obstacles": obstacles,
            "width": 10,
            "height": 10
        }
        msg = String()
        msg.data = json.dumps(request_data)
        self.publisher_.publish(msg)
        self.get_logger().info(f"📤 Sent request: {msg.data}")

@pytest.fixture(scope="module")
def ros_context():
    """初始化 ROS 2 上下文"""
    rclpy.init()
    yield
    rclpy.shutdown()

def run_node_in_thread(node):
    rclpy.spin(node)

def test_simple_path(ros_context):
    """测试 1: 简单的无障碍路径规划"""
    tester = PathPlannerTester()
    
    # 在单独线程中运行 spin，以便接收回调
    spin_thread = threading.Thread(target=run_node_in_thread, args=(tester,), daemon=True)
    spin_thread.start()
    
    # 发送请求: 从 (0,0) 到 (2,2)，无障碍
    # 期望路径可能是: (0,0)->(1,0)->(2,0)->(2,1)->(2,2) 或其他等长路径
    tester.send_request(start=[0,0], goal=[2,2], obstacles=[])
    
    # 等待响应 (最多 5 秒)
    timeout = 5.0
    start_time = time.time()
    while tester.received_response is None:
        if time.time() - start_time > timeout:
            pytest.fail("Timeout waiting for path response")
        time.sleep(0.1)
        
    response = tester.received_response
    assert response['status'] == 'success', "Should find a path"
    path = response['path']
    assert len(path) > 0, "Path should not be empty"
    assert tuple(path[0]) == (0,0), "Start point mismatch"
    assert tuple(path[-1]) == (2,2), "Goal point mismatch"
    
    tester.get_logger().info(f"✅ Simple Path Test Passed: {path}")

def test_obstacle_avoidance(ros_context):
    """测试 2: 障碍物绕行"""
    tester = PathPlannerTester()
    
    spin_thread = threading.Thread(target=run_node_in_thread, args=(tester,), daemon=True)
    spin_thread.start()
    
    # 发送请求: 从 (0,0) 到 (0,2)，中间 (0,1) 有障碍物
    # 期望绕行: (0,0) -> (1,0) -> (1,1) -> (1,2) -> (0,2) (示例)
    tester.send_request(start=[0,0], goal=[0,2], obstacles=[[0,1]])
    
    timeout = 5.0
    start_time = time.time()
    while tester.received_response is None:
        if time.time() - start_time > timeout:
            pytest.fail("Timeout waiting for path response")
        time.sleep(0.1)
        
    response = tester.received_response
    assert response['status'] == 'success', "Should find a path around obstacle"
    path = response['path']
    
    # 验证没有穿过障碍物 (0,1)
    for point in path:
        assert tuple(point) != (0,1), "Path hit the obstacle!"
        
    tester.get_logger().info(f"✅ Obstacle Test Passed: {path}")

if __name__ == '__main__':
    # 提示: 运行此测试前需要先启动 path_planner_node
    # ros2 run cloud_monitor_pkg path_planner_node
    print("⚠️  Ensure 'path_planner_node' is running before executing tests!")
    pytest.main([__file__, "-v"])