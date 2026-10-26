"""Convert a fresh safe Ackermann command to the Gazebo body velocity."""

import math

from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile


def convert_command(message, now_ns):
    """Return a new Twist and a rejection reason, using simulation nanoseconds."""
    result = Twist()
    drive = message.drive
    values = (drive.speed, drive.steering_angle, drive.steering_angle_velocity,
              drive.acceleration, drive.jerk)
    if not all(math.isfinite(value) for value in values):
        return result, 'non_finite'
    stamp_ns = message.header.stamp.sec * 1_000_000_000 + message.header.stamp.nanosec
    if now_ns - stamp_ns > 250_000_000:
        return result, 'stale_command'
    speed = max(0.0, min(drive.speed, 1.2))
    steering = max(-0.45, min(drive.steering_angle, 0.45))
    result.linear.x = speed
    result.angular.z = speed * math.tan(steering) / 0.8
    return result, ''


class DriveAdapter(Node):
    """Subscribe only to the safe boundary and publish one result per input."""

    def __init__(self):
        super().__init__('drive_adapter')
        self.declare_parameter('input_topic', '/drive/safe')
        self.declare_parameter('output_topic', '/vehicle/gz_cmd_vel')
        qos = QoSProfile(depth=10)
        self.publisher = self.create_publisher(
            Twist, self.get_parameter('output_topic').value, qos)
        self.subscription = self.create_subscription(
            AckermannDriveStamped, self.get_parameter('input_topic').value,
            self.on_command, qos)

    def on_command(self, message):
        result, reason = convert_command(message, self.get_clock().now().nanoseconds)
        if reason:
            self.get_logger().warning('Rejected command: ' + reason + '; publishing zero Twist')
        self.publisher.publish(result)


def main(args=None):
    rclpy.init(args=args)
    node = DriveAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
