import math
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
import xacro


MODEL = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'
SENSORS = ('camera', 'lidar', 'imu')
WHEELS = ('front_left', 'front_right', 'rear_left', 'rear_right')


def model(**parameters):
    mappings = {name: str(value) for name, value in parameters.items()}
    return ET.fromstring(xacro.process_file(str(MODEL), mappings=mappings).toxml())


def numbers(text):
    return tuple(float(value) for value in text.split())


def test_connected_tree():
    root = model()
    links = [link.get('name') for link in root.findall('link')]
    joints = root.findall('joint')
    assert len(links) == len(set(links))
    names = [joint.get('name') for joint in joints]
    assert len(names) == len(set(names))
    assert len(joints) == len(links) - 1
    parents = {}
    for joint in joints:
        parent = joint.find('parent').get('link')
        child = joint.find('child').get('link')
        assert parent in links and child in links
        assert child not in parents
        parents[child] = parent
    assert set(links) - set(parents) == {'base_link'}
    for link in links:
        seen = set()
        current = link
        while current in parents:
            assert current not in seen, 'Cycle in the link tree'
            seen.add(current)
            current = parents[current]
        assert current == 'base_link'


@pytest.mark.parametrize('sensor', SENSORS)
def test_sensor_contract(sensor):
    root = model()
    assert root.find(f"link[@name='{sensor}_link']") is not None
    joint = root.find(f"joint[@name='{sensor}_joint']")
    assert joint is not None
    assert joint.get('type') == 'fixed'
    assert joint.find('parent').get('link') == 'base_link'
    assert joint.find('child').get('link') == f'{sensor}_link'
    assert numbers(joint.find('origin').get('xyz')) == pytest.approx((0.28, 0, 0.38))
    assert numbers(joint.find('origin').get('rpy', '0 0 0')) == pytest.approx((0, 0, 0))


@pytest.mark.parametrize('wb,tr,radius', [(0.8, 0.62, 0.12), (1.0, 0.7, 0.15)])
def test_wheel_parameters(wb, tr, radius):
    root = model(wheelbase=wb, track=tr, wheel_radius=radius)
    for wheel in WHEELS:
        front = wheel.startswith('front')
        left = wheel.endswith('left')
        link = root.find(f"link[@name='{wheel}_wheel']")
        joint = root.find(f"joint[@name='{wheel}_wheel_joint']")
        assert joint.get('type') == 'continuous'
        assert numbers(joint.find('axis').get('xyz')) == (0, 1, 0)
        if front:
            assert joint.find('parent').get('link') == f'{wheel}_knuckle'
            assert numbers(joint.find('origin').get('xyz')) == (0, 0, 0)
            steering = root.find(f"joint[@name='{wheel}_steering_joint']")
            assert steering.get('type') == 'revolute'
            assert steering.find('parent').get('link') == 'base_link'
            assert steering.find('child').get('link') == f'{wheel}_knuckle'
            assert numbers(steering.find('axis').get('xyz')) == (0, 0, 1)
            limits = steering.find('limit')
            assert float(limits.get('lower')) < 0 < float(limits.get('upper'))
            assert float(limits.get('effort')) > 0
            assert float(limits.get('velocity')) > 0
            origin = steering.find('origin')
        else:
            assert joint.find('parent').get('link') == 'base_link'
            origin = joint.find('origin')
        expected = (wb / 2 if front else -wb / 2, tr / 2 if left else -tr / 2, 0)
        assert numbers(origin.get('xyz')) == pytest.approx(expected)
        for category in ('visual', 'collision'):
            cylinder = link.find(f'{category}/geometry/cylinder')
            assert float(cylinder.get('radius')) == pytest.approx(radius)
            assert float(cylinder.get('length')) == pytest.approx(0.07)
            rotation = link.find(f'{category}/origin').get('rpy')
            assert numbers(rotation) == pytest.approx((math.pi / 2, 0, 0))


def test_body_geometry():
    root = model()
    body = root.find("link[@name='base_link']")
    for category in ('visual', 'collision'):
        size = body.find(f'{category}/geometry/box').get('size')
        assert numbers(size) == pytest.approx((1.05, 0.52, 0.22))
        assert numbers(body.find(f'{category}/origin').get('xyz')) == (0, 0, 0.12)


def test_physical_values():
    root = model()
    for link in root.findall('link'):
        for category in ('visual', 'collision'):
            geometry = link.find(f'{category}/geometry')
            assert geometry is not None
            box = geometry.find('box')
            cylinder = geometry.find('cylinder')
            if box is not None:
                dimensions = numbers(box.get('size'))
            else:
                assert cylinder is not None
                dimensions = (float(cylinder.get('radius')), float(cylinder.get('length')))
            assert all(math.isfinite(value) and value > 0 for value in dimensions)
        inertial = link.find('inertial')
        mass = float(inertial.find('mass').get('value'))
        assert math.isfinite(mass) and mass > 0
        inertia = inertial.find('inertia')
        diagonal = [float(inertia.get(name)) for name in ('ixx', 'iyy', 'izz')]
        assert all(math.isfinite(value) and value > 0 for value in diagonal)
        assert all(float(inertia.get(name)) == 0 for name in ('ixy', 'ixz', 'iyz'))
        assert 2 * max(diagonal) <= sum(diagonal) + 1e-12
