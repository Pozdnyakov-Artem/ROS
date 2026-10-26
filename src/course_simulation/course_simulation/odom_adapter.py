"""Normalize Gazebo odometry and own the single odom -> base_link TF."""

from copy import deepcopy
import math

from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from tf2_ros import TransformBroadcaster


def normalize_odometry(message):
    """Copy valid odometry without changing its timestamp or measured fields."""
    if (message.header.frame_id != 'course_ackermann/odom'
            or message.child_frame_id != 'course_ackermann/base_link'):
        raise ValueError('unexpected_frames')
    position = message.pose.pose.position
    orientation = message.pose.pose.orientation
    linear = message.twist.twist.linear
    angular = message.twist.twist.angular
    values = [position.x, position.y, position.z,
              orientation.x, orientation.y, orientation.z, orientation.w,
              linear.x, linear.y, linear.z, angular.x, angular.y, angular.z]
    values.extend(message.pose.covariance)
    values.extend(message.twist.covariance)
    if not all(math.isfinite(value) for value in values):
        raise ValueError('non_finite_odometry')
    result = deepcopy(message)
    result.header.frame_id = 'odom'
    result.child_frame_id = 'base_link'
    transform = TransformStamped()
    transform.header = deepcopy(result.header)
    transform.child_frame_id = result.child_frame_id
    transform.transform.translation.x = position.x
    transform.transform.translation.y = position.y
    transform.transform.translation.z = position.z
    transform.transform.rotation = deepcopy(orientation)
    return result, transform


class OdomAdapter(Node):
    """Publish normalized odometry and the matching dynamic transform."""

    def __init__(self):
        super().__init__('odom_adapter')
        self.declare_parameter('input_topic', '/vehicle/odom_gz')
        self.declare_parameter('output_topic', '/vehicle/odom')
        qos = QoSProfile(depth=10)
        self.publisher = self.create_publisher(
            Odometry, self.get_parameter('output_topic').value, qos)
        self.broadcaster = TransformBroadcaster(self)
        self.subscription = self.create_subscription(
            Odometry, self.get_parameter('input_topic').value, self.on_odometry, qos)

    def on_odometry(self, message):
        try:
            result, transform = normalize_odometry(message)
        except ValueError as error:
            self.get_logger().warning('Rejected odometry: ' + str(error))
            return
        self.publisher.publish(result)
        self.broadcaster.sendTransform(transform)


def main(args=None):
    rclpy.init(args=args)
    node = OdomAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
