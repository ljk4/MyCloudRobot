import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import heapq

class PathPlannerNode(Node):
    def __init__(self):
        super().__init__('path_planner')
        # 订阅前端发来的寻路请求
        self.subscription = self.create_subscription(
            String,
            'game_request', 
            self.listener_callback,
            10)
        # 发布寻路结果
        self.publisher_ = self.create_publisher(String, 'game_response', 10)
        self.get_logger().info('🕹️ 2D Pathfinding Game Backend Ready!')

    def listener_callback(self, msg):
        try:
            # 解析 JSON 数据: { "start": [x,y], "goal": [x,y], "obstacles": [[x,y],...], "width": 20, "height": 20 }
            data = json.loads(msg.data)
            start = tuple(data['start'])
            goal = tuple(data['goal'])
            # 将障碍物列表转换为集合，方便快速查找
            obstacles = set(tuple(o) for o in data['obstacles'])
            width = data.get('width', 20)
            height = data.get('height', 20)

            self.get_logger().info(f'Received path request: Start={start}, Goal={goal}')

            path = self.astar(start, goal, obstacles, width, height)
            
            result = {}
            if path:
                result['status'] = 'success'
                result['path'] = path
                self.get_logger().info(f'Path found with length {len(path)}')
            else:
                result['status'] = 'no_path'
                self.get_logger().info('No path found')
            
            response_msg = String()
            response_msg.data = json.dumps(result)
            self.publisher_.publish(response_msg)
            
        except Exception as e:
            self.get_logger().error(f'Error processing path request: {str(e)}')

    def heuristic(self, a, b):
        # 曼哈顿距离
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node, width, height):
        # 上下左右
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        result = []
        for d in directions:
            neighbor = (node[0] + d[0], node[1] + d[1])
            if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height:
                result.append(neighbor)
        return result

    def astar(self, start, goal, obstacles, width, height):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        open_set_hash = {start}

        while open_set:
            current = heapq.heappop(open_set)[1]
            open_set_hash.remove(current)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current, width, height):
                if neighbor in obstacles:
                    continue
                
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
        
        return None

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1] # Reverse

def main(args=None):
    rclpy.init(args=args)
    node = PathPlannerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
