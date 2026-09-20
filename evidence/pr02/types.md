# /turtle1/cmd_vel
Тип:
```bash
ros2 topic type /turtle1/cmd_vel
```
Вывод:
```text
geometry_msgs/msg/Twist
```
Поля:
```bash
ros2 interface show geometry_msgs/msg/Twist
```
Вывод:
```text
# This expresses velocity in free space broken into its linear and angular parts.

Vector3  linear
        float64 x
        float64 y
        float64 z
Vector3  angular
        float64 x
        float64 y
        float64 z
```
Линейная скорость по 3 осям и угловая скорость по 3 осям
# /turtle1/pose
Тип:
```bash
ros2 topic type /turtle1/pose
```
Вывод:
```text
turtlesim/msg/Pose
```
Поля:
```bash
ros2 interface show turtlesim/msg/Pose
```
Вывод:
```text
float32 x
float32 y
float32 theta

float32 linear_velocity
float32 angular_velocity
```
Координаты по x y, направление в радианах, линейная и угловая скорость