import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose

sensor_qos = QoSProfile(
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
)


class PoseSubscriber(Node):
    def __init__(self):
        super().__init__('pose_subscriber')
        self.declare_parameter('reliability', 'reliable')
        self.reliability = self.get_parameter('reliability').value
        policies = {
            'reliable': ReliabilityPolicy.RELIABLE,
            'best_effort': ReliabilityPolicy.BEST_EFFORT,
        }
        if self.reliability not in policies:
            self.destroy_node()
            raise ValueError('reliability must be reliable or best_effort')

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=policies[self.reliability],
            durability=DurabilityPolicy.VOLATILE,
        )
        self.received = 0
        self.subscription = self.create_subscription(
            Pose, 'sensor_pose', self.on_pose, qos)
        self.timer = self.create_timer(1.0, self.log_count)
        self.get_logger().info(f'Reliability: {self.reliability}')

    def on_pose(self, message):
        self.received += 1

    def log_count(self):
        self.get_logger().info(
            f'reliability={self.reliability} received={self.received}')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = PoseSubscriber()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
