import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool, Trigger

class ParamServiceNode(Node):
    def __init__(self):
        super().__init__('param_service_node')
        self.declare_parameter('robot.max_speed', 0.5)
        self.declare_parameter('robot.safety_mode', False)
        
        self.srv_safe = self.create_service(SetBool, 'set_safety_mode', self.cb_safe)
        self.srv_reset = self.create_service(Trigger, 'reset_robot', self.cb_reset)
        self.get_logger().info("⚙️ Param Service Ready")

    def cb_safe(self, req, res):
        mode = req.data
        self.set_parameters([rclpy.parameter.Parameter('robot.safety_mode', value=mode)])
        speed = 0.2 if mode else 0.8
        self.set_parameters([rclpy.parameter.Parameter('robot.max_speed', value=speed)])
        res.success = True
        res.message = f"Switched to {'SAFE' if mode else 'NORMAL'} (Speed: {speed})"
        self.get_logger().warn(res.message)
        return res

    def cb_reset(self, req, res):
        self.set_parameters([rclpy.parameter.Parameter('robot.safety_mode', value=False)])
        self.set_parameters([rclpy.parameter.Parameter('robot.max_speed', value=0.5)])
        res.success = True
        res.message = "Params Reset"
        return res

def main(args=None):
    rclpy.init(args=args)
    node = ParamServiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()