from copy import deepcopy
import math

from nav_msgs.msg import Odometry
import pytest

from course_simulation.odom_adapter import normalize_odometry


def odometry():
    message = Odometry()
    message.header.stamp.sec = 12
    message.header.stamp.nanosec = 345678901
    message.header.frame_id = 'course_ackermann/odom'
    message.child_frame_id = 'course_ackermann/base_link'
    message.pose.pose.position.x = 1.25
    message.pose.pose.position.y = -0.4
    message.pose.pose.orientation.z = math.sin(0.2)
    message.pose.pose.orientation.w = math.cos(0.2)
    message.twist.twist.linear.x = 0.5
    message.twist.twist.angular.z = 0.1
    message.pose.covariance = [float(index) / 100.0 for index in range(36)]
    message.twist.covariance = [float(index) / 200.0 for index in range(36)]
    return message


def test_frames_stamp_pose_twist_covariance_and_input_unchanged():
    source = odometry()
    before = deepcopy(source)
    result, transform = normalize_odometry(source)
    assert source == before
    assert result.header.frame_id == 'odom'
    assert result.child_frame_id == 'base_link'
    assert result.header.stamp == source.header.stamp == transform.header.stamp
    assert result.pose == source.pose
    assert result.twist == source.twist
    assert transform.header.frame_id == 'odom'
    assert transform.child_frame_id == 'base_link'
    assert transform.transform.translation.x == source.pose.pose.position.x
    assert transform.transform.translation.y == source.pose.pose.position.y
    assert transform.transform.translation.z == source.pose.pose.position.z
    assert transform.transform.rotation == source.pose.pose.orientation


@pytest.mark.parametrize('parent,child', [
    ('odom', 'base_link'), ('other/odom', 'course_ackermann/base_link'),
    ('course_ackermann/odom', 'other/base_link'),
])
def test_reject_unexpected_frames(parent, child):
    message = odometry()
    message.header.frame_id = parent
    message.child_frame_id = child
    with pytest.raises(ValueError, match='unexpected_frames'):
        normalize_odometry(message)


@pytest.mark.parametrize('field', ['position', 'orientation', 'linear', 'angular', 'pose_cov', 'twist_cov'])
@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_reject_non_finite(field, value):
    message = odometry()
    if field == 'position':
        message.pose.pose.position.x = value
    elif field == 'orientation':
        message.pose.pose.orientation.w = value
    elif field == 'linear':
        message.twist.twist.linear.x = value
    elif field == 'angular':
        message.twist.twist.angular.z = value
    elif field == 'pose_cov':
        message.pose.covariance[4] = value
    else:
        message.twist.covariance[4] = value
    with pytest.raises(ValueError, match='non_finite_odometry'):
        normalize_odometry(message)
