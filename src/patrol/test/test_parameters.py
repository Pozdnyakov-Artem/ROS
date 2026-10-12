from patrol.patrol import command_from_pose, Patrol, validate_values
import pytest
import rclpy
from rclpy.parameter import Parameter
from turtlesim.msg import Pose


@pytest.mark.parametrize('values', [
    (10.0, 0.5, 0.3), (5.0, 0.5, 0.3),
    (1.0, 0.0, -1.0), (30.0, 1.0, 1.0),
])
def test_valid_values(values):
    assert validate_values(*values) == (True, '')


@pytest.mark.parametrize('index', [0, 1, 2])
@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf'),
                                   True, '5.0'])
def test_non_finite_and_non_numeric_values(index, value):
    values = [10.0, 0.5, 0.3]
    values[index] = value
    ok, reason = validate_values(*values)
    assert not ok
    assert reason


@pytest.mark.parametrize('values', [
    (0.0, 0.5, 0.3), (-1.0, 0.5, 0.3), (31.0, 0.5, 0.3),
    (10.0, -0.1, 0.3), (10.0, 1.1, 0.3),
    (10.0, 0.5, -1.1), (10.0, 0.5, 1.1),
])
def test_out_of_range_values(values):
    ok, reason = validate_values(*values)
    assert not ok
    assert reason


@pytest.fixture
def node():
    rclpy.init()
    patrol = Patrol()
    try:
        yield patrol
    finally:
        patrol.destroy_node()
        rclpy.try_shutdown()


def test_frequency_replaces_timer_and_stops_old_one(node):
    old_timer = node.timer
    result = node.set_parameters_atomically([Parameter('publish_hz', value=5.0)])
    assert result.successful
    assert node.get_parameter('publish_hz').value == 5.0
    assert node.publish_hz == 5.0
    assert node.timer is not old_timer
    assert old_timer not in node.timers
    assert len(list(node.timers)) == 1
    assert node.timer.timer_period_ns == 200_000_000
    assert not node.timer.is_canceled()


@pytest.mark.parametrize('value', [0.0, -1.0, float('nan')])
def test_invalid_frequency_preserves_active_state(node, value):
    node.set_parameters_atomically([Parameter('publish_hz', value=5.0)])
    old_timer = node.timer
    result = node.set_parameters_atomically([
        Parameter('publish_hz', value=value),
        Parameter('linear_speed', value=0.8),
    ])
    assert not result.successful
    assert result.reason
    assert node.get_parameter('publish_hz').value == 5.0
    assert node.get_parameter('linear_speed').value == 0.5
    assert node.publish_hz == 5.0
    assert node.linear_speed == 0.5
    assert node.timer is old_timer
    assert node.timer.timer_period_ns == 200_000_000
    assert not node.timer.is_canceled()
    assert len(list(node.timers)) == 1


def test_speed_and_turn_change_command_without_replacing_timer(node):
    old_timer = node.timer
    result = node.set_parameters_atomically([
        Parameter('linear_speed', value=0.8),
        Parameter('turn_rate', value=-0.4),
    ])
    assert result.successful
    assert node.timer is old_timer
    command = command_from_pose(Pose(), node.turn_rate, node.linear_speed)
    assert command.linear.x == pytest.approx(0.8)
    assert command.angular.z == pytest.approx(-0.4)


def test_same_frequency_keeps_timer(node):
    old_timer = node.timer
    result = node.set_parameters_atomically([Parameter('publish_hz', value=10.0)])
    assert result.successful
    assert node.timer is old_timer


def test_startup_overrides_are_applied():
    rclpy.init(args=['--ros-args', '-p', 'publish_hz:=5.0',
                     '-p', 'linear_speed:=0.8', '-p', 'turn_rate:=-0.4'])
    patrol = None
    try:
        patrol = Patrol()
        assert patrol.publish_hz == 5.0
        assert patrol.linear_speed == 0.8
        assert patrol.turn_rate == -0.4
        assert patrol.timer.timer_period_ns == 200_000_000
    finally:
        if patrol is not None:
            patrol.destroy_node()
        rclpy.try_shutdown()


def test_invalid_startup_frequency_is_rejected():
    rclpy.init(args=['--ros-args', '-p', 'publish_hz:=0.0'])
    try:
        with pytest.raises(ValueError, match='publish_hz'):
            Patrol()
    finally:
        rclpy.try_shutdown()
