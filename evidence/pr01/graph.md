# Домен
16

Команда:
```bash
ros2 node list --no-daemon --spin-time 2
```
Результат:
```
/teleop_turtle
/turtlesim
```

Команда:
```bash
ros2 topic list -t
```
Результат:
```
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

Команда:
```bash
ros2 node info /turtlesim
```
Результат:
```
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```

Команда:
```bash
ros2 topic type /turtle1/pose
```
Результат:
```
turtlesim/msg/Pose
```
Команда:
```bash
ros2 topic echo /turtle1/pose --once
```
Результат:
```yaml
x: 5.902738571166992
y: 6.29534387588501
theta: -2.0160000324249268
linear_velocity: 2.0
angular_velocity: 0.0
```

Команда:
```bash
ros2 topic hz /turtle1/pose
```
Результат:
```text
WARNING: topic [/turtle1/pose] does not appear to be published yet
average rate: 62.468
        min: 0.014s max: 0.018s std dev: 0.00064s window: 64
average rate: 62.501
        min: 0.014s max: 0.018s std dev: 0.00058s window: 127
average rate: 62.495
        min: 0.014s max: 0.018s std dev: 0.00059s window: 190
average rate: 62.491
        min: 0.014s max: 0.018s std dev: 0.00062s window: 253
average rate: 62.484
        min: 0.014s max: 0.018s std dev: 0.00062s window: 316
average rate: 62.499
        min: 0.013s max: 0.019s std dev: 0.00064s window: 379
average rate: 62.500
        min: 0.013s max: 0.019s std dev: 0.00065s window: 442
average rate: 62.493
        min: 0.013s max: 0.019s std dev: 0.00066s window: 505
average rate: 62.499
        min: 0.013s max: 0.019s std dev: 0.00065s window: 568
average rate: 62.498
        min: 0.013s max: 0.019s std dev: 0.00064s window: 631
average rate: 62.499
        min: 0.013s max: 0.019s std dev: 0.00064s window: 694
average rate: 62.490
        min: 0.013s max: 0.019s std dev: 0.00066s window: 757
average rate: 62.497
        min: 0.013s max: 0.019s std dev: 0.00066s window: 820
average rate: 62.496
        min: 0.013s max: 0.019s std dev: 0.00066s window: 883
average rate: 62.492
        min: 0.013s max: 0.019s std dev: 0.00067s window: 946
average rate: 62.499
        min: 0.013s max: 0.019s std dev: 0.00066s window: 1009
average rate: 62.501
        min: 0.013s max: 0.019s std dev: 0.00066s window: 1072
average rate: 62.498
        min: 0.013s max: 0.019s std dev: 0.00065s window: 1135
average rate: 62.495
        min: 0.013s max: 0.019s std dev: 0.00065s window: 1198
average rate: 62.495
        min: 0.013s max: 0.019s std dev: 0.00065s window: 1261
average rate: 62.498
        min: 0.013s max: 0.019s std dev: 0.00066s window: 1324
average rate: 62.497
        min: 0.013s max: 0.019s std dev: 0.00066s window: 1387
average rate: 62.497
        min: 0.013s max: 0.019s std dev: 0.00066s window: 1450
average rate: 62.497
        min: 0.013s max: 0.019s std dev: 0.00066s window: 1513
average rate: 60.943
        min: 0.013s max: 0.644s std dev: 0.01603s window: 1537
```
# Ноды
* /turtlesim - симулятор
* /teleop_turtle - управление с клавиатуры
# Топики и типы:
- `/parameter_events` - `rcl_interfaces/msg/ParameterEvent`
- `/rosout` - `rcl_interfaces/msg/Log`
- `/turtle1/cmd_vel` - `geometry_msgs/msg/Twist`
- `/turtle1/color_sensor` - `turtlesim/msg/Color`
- `/turtle1/pose` - `turtlesim/msg/Pose`

По `ros2 node info /turtlesim`: симулятор подписан на
`/turtle1/cmd_vel` и публикует `/turtle1/pose` и
`/turtle1/color_sensor`. Команда `ros2 topic echo /turtle1/pose --once`
получила сообщение с координатами и скоростями черепахи.

Частота `/turtle1/pose`: примерно 62,5 Гц, замер около 25 секунд.

# Домен
17

Команда:
```bash
ros2 node list --no-daemon --spin-time 2
```
Результат:
```
/teleop_turtle
```

Команды:
```bash
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```
Результат:
```text
exit=124
```

# Домен
16

Команда:
```bash
ros2 node list --no-daemon --spin-time 2
```
Результат:
```text
/teleop_turtle
/turtlesim
```

Команды:
```bash
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?"
```
Результат:
```text
exit=0
```

# Сравнение «до / сбой / после»
| Состояние | Домен turtlesim | Домен teleop и наблюдателя | Обнаруженные ноды | Результат чтения позы |
|---|---:|---:|---|---|
| До сбоя | 16 | 16 | `/turtlesim`, `/teleop_turtle` | Поза поступает |
| Сбой | 16 | 17 | `/teleop_turtle` | Поза не поступила за 5 секунд, `exit=124` |
| После восстановления | 16 | 16 | `/turtlesim`, `/teleop_turtle` | Поза поступила, `exit=0` |

# Объяснение
`ROS_DOMAIN_ID` применяется при запуске процесса. Изменение переменной
в терминале не переносит уже запущенную ноду в другой домен, поэтому
`/teleop_turtle` требовалось остановить и запустить заново. Симулятор
уже работал в исходном домене 16, поэтому перезапускать его не пришлось.
Переустановка ROS также не требовалась: причиной сбоя была изоляция
участников разными доменами, а не неисправность ROS.