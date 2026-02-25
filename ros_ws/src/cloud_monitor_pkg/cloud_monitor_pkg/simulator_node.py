import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

class SimulatorNode(Node):
    def __init__(self):
        super().__init__('simulator_node')
        self.scan_pub = self.create_publisher(LaserScan, 'scan', 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.timer = self.create_timer(0.1, self.tick)
        self.t = 0.0
        self.get_logger().info("🤖 Simulator Started")

    def tick(self):
        # Publish Scan
        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = "laser_link"
        scan.angle_min = -math.pi
        scan.angle_max = math.pi
        scan.angle_increment = math.pi / 180.0
        scan.range_min = 0.1
        scan.range_max = 10.0
        scan.ranges = [max(0.1, 5.0 + 2.0 * math.sin(self.t * 0.5 + i * 0.1)) for i in range(360)]
        self.scan_pub.publish(scan)

        # Publish Odom
        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = "odom"
        odom.pose.pose.position.x = 5.0 * math.cos(self.t * 0.2)
        odom.pose.pose.position.y = 5.0 * math.sin(self.t * 0.2)
        odom.pose.pose.orientation.w = 1.0
        self.odom_pub.publish(odom)
        self.t += 0.1

def main(args=None):
    rclpy.init(args=args)
    node = SimulatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()