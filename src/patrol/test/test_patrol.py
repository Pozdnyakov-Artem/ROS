from patrol.patrol import command_from_pose
import pytest
from turtlesim.msg import Pose


def test_command_without_pose_is_zero():
    command = command_from_pose(None)

    assert command.linear.x == pytest.approx(0.0)
    assert command.angular.z == pytest.approx(0.0)


def test_command_after_pose_moves_turtle():
    pose = Pose()
    pose.x = 5.0
    pose.y = 5.0
    pose.theta = 0.0

    command = command_from_pose(pose)

    assert command.linear.x == pytest.approx(0.5)
    assert command.angular.z == pytest.approx(0.3)
