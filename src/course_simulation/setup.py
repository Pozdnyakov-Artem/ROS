from pathlib import Path

from setuptools import find_packages, setup


package_name = 'course_simulation'
data_files = [
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
]
for directory in ('launch', 'config', 'models', 'worlds'):
    for path in sorted(Path(directory).rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            data_files.append(('share/' + package_name + '/' + str(path.parent), [str(path)]))

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='owner',
    maintainer_email='a.pozdnyakov1@g.nsu.ru',
    description='Headless course simulation with Ackermann and odometry adapters.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={'console_scripts': [
        'drive_adapter = course_simulation.drive_adapter:main',
        'odom_adapter = course_simulation.odom_adapter:main',
    ]},
)
