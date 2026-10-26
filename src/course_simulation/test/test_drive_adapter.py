import math

from ackermann_msgs.msg import AckermannDriveStamped
import pytest

from course_simulation.drive_adapter import convert_command


def command(speed=0.8, steering=0.0):
    message = AckermannDriveStamped()
    message.header.stamp.sec = 10
    message.drive.speed = speed
    message.drive.steering_angle = steering
    return message


def test_straight():
    result, reason = convert_command(command(), 10_100_000_000)
    assert reason == ''
    assert result.linear.x == pytest.approx(0.8)
    assert result.angular.z == 0.0


@pytest.mark.parametrize('angle', [-0.3, 0.3])
def test_turn(angle):
    result, reason = convert_command(command(0.8, angle), 10_000_000_000)
    assert reason == ''
    assert result.angular.z == pytest.approx(0.8 * math.tan(angle) / 0.8)


def test_zero_speed_cannot_turn_in_place():
    result, reason = convert_command(command(0.0, 0.4), 10_000_000_000)
    assert reason == ''
    assert result.linear.x == result.angular.z == 0.0


@pytest.mark.parametrize('speed,angle,v,delta', [
    (-1.0, 0.3, 0.0, 0.3), (3.0, 2.0, 1.2, 0.45), (0.6, -2.0, 0.6, -0.45),
])
def test_limits(speed, angle, v, delta):
    result, reason = convert_command(command(speed, angle), 10_000_000_000)
    assert reason == ''
    assert result.linear.x == pytest.approx(v)
    assert result.angular.z == pytest.approx(v * math.tan(delta) / 0.8)


@pytest.mark.parametrize('age_ns,expected', [(250_000_000, ''), (250_000_001, 'stale_command')])
def test_age_boundary(age_ns, expected):
    result, reason = convert_command(command(), 10_000_000_000 + age_ns)
    assert reason == expected
    if reason:
        assert result.linear.x == result.angular.z == 0.0


@pytest.mark.parametrize('field', [
    'speed', 'steering_angle', 'steering_angle_velocity', 'acceleration', 'jerk',
])
@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_non_finite(field, value):
    message = command()
    setattr(message.drive, field, value)
    result, reason = convert_command(message, 10_000_000_000)
    assert reason == 'non_finite'
    assert result.linear.x == result.angular.z == 0.0


def test_rejected_command_does_not_reuse_previous_twist():
    accepted, _ = convert_command(command(1.0, 0.3), 10_000_000_000)
    rejected, reason = convert_command(command(), 11_000_000_000)
    assert accepted.linear.x > 0.0
    assert reason == 'stale_command'
    assert rejected.linear.x == rejected.angular.z == 0.0
