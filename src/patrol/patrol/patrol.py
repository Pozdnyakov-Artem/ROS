import math

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


def command_from_pose(pose, turn_rate=0.3, linear_speed=0.5):
    command = Twist()

    if pose is not None:
        command.linear.x = linear_speed
        command.angular.z = turn_rate

    return command


def validate_values(publish_hz, linear_speed, turn_rate):
    checks = (
        ('publish_hz', publish_hz, 1.0, 30.0),
        ('linear_speed', linear_speed, 0.0, 1.0),
        ('turn_rate', turn_rate, -1.0, 1.0),
    )

    for name, value, minimum, maximum in checks:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f'{name}: ожидается число'

        if not math.isfinite(value):
            return False, f'{name}: значение должно быть конечным'

        if not minimum <= value <= maximum:
            return False, (
                f'{name}: значение должно быть от {minimum} до {maximum}'
            )

    return True, ''


class Patrol(Node):

    def __init__(self):
        super().__init__('patrol')
        self.latest_pose = None
        self.declare_parameter('publish_hz', 10.0)
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)

        self.publish_hz = self.get_parameter('publish_hz').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.turn_rate = self.get_parameter('turn_rate').value
        ok, reason = validate_values(
            self.publish_hz, self.linear_speed, self.turn_rate)
        if not ok:
            self.destroy_node()
            raise ValueError(reason)

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.on_pose,
            10,
        )

        self.command_publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_hz,
            self.timer_callback,
        )

        self.add_on_set_parameters_callback(self.validate)
        self.add_post_set_parameters_callback(self.apply)

    def apply(self, updates):
        proposed = {p.name: p.value for p in updates}

        new_hz = proposed.get('publish_hz', self.publish_hz)

        if new_hz != self.publish_hz:
            self.timer.cancel()
            self.destroy_timer(self.timer)
            self.timer = self.create_timer(
                1.0 / new_hz,
                self.timer_callback,
            )

        self.publish_hz = new_hz
        self.linear_speed = proposed.get('linear_speed', self.linear_speed)
        self.turn_rate = proposed.get('turn_rate', self.turn_rate)

    def validate(self, updates):
        proposed = {p.name: p.value for p in updates}
        ok, reason = validate_values(
            proposed.get('publish_hz', self.publish_hz),
            proposed.get('linear_speed', self.linear_speed),
            proposed.get('turn_rate', self.turn_rate))
        return SetParametersResult(successful=ok, reason=reason)

    def on_pose(self, message):
        self.latest_pose = message

    def timer_callback(self):
        command = command_from_pose(self.latest_pose, self.turn_rate, self.linear_speed)
        self.command_publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)

    node = None
    try:
        node = Patrol()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
