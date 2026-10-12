import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


class PoseRelay(Node):
    def __init__(self):
        super().__init__('pose_replay')
        sensor_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.publisher = self.create_publisher(
            Pose, 'sensor_pose', sensor_qos)
        self.subscription = self.create_subscription(
            Pose, 'pose', self.on_pose, 10)

    def on_pose(self, message):
        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = PoseRelay()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
