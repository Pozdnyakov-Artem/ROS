# Создание пакета
```bash
ros2 pkg create \
  --build-type ament_python \
  --node-name patrol \
  patrol \
  --dependencies rclpy geometry_msgs
```
Создание пакета
`--build-type ament_python` - пакет на Python
`--node-name patrol` - создаёт исполняемую команду с таким именем
`patrol` - создаёт ROS пакет с таким именем
`rclpy` - Python-библиотека ROS 2
`geometry_msgs` - содержит тип Twist

```bash
colcon build --symlink-install --packages-select patrol
```
Сборка пакета
`--symlink-install` - создать символические ссылки из install/
`--packages-select patrol` - собрать только пакет patrol
# Проверка регистрации
```bash
ros2 pkg executables patrol
```
спрашивает индекс установленных ROS-пакетов

# Тест с поломкой
Терминал А
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

Терминал B
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 run patrol patrol
```

Терминал C
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
```
Команда:
```bash
ros2 node info /patrol
```
Вывод:
```text
/patrol
  Subscribers:
    /turtle1/pose: turtlesim/msg/Pose
  Publishers:
    /cmd_vel: geometry_msgs/msg/Twist
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
  Service Servers:
    /patrol/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /patrol/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /patrol/get_parameters: rcl_interfaces/srv/GetParameters
    /patrol/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /patrol/list_parameters: rcl_interfaces/srv/ListParameters
    /patrol/set_parameters: rcl_interfaces/srv/SetParameters
    /patrol/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:

  Action Clients:
```

Команда:
```bash
ros2 topic info /cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 0

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.eb.7d.61.28.0a.9d.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

Команда:
```bash
ros2 topic info /turtle1/cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: patrol
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.eb.7d.13.86.c7.ba.00.00.00.00.00.00.14.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 0
```

# Объяснение
Публикация идёт в относительный cmd_vel, не соединённый с /turtle1/cmd_vel

`rclpy.init()` инициализирует ROS-контекст до создания ноды.
`rclpy.spin(node)` запускает цикл обработки событий. Пока выполняется `spin`,
ROS вызывает callback подписки при поступлении позы и callback таймера каждые
0,1 секунды.
Callback подписки `on_pose` получает сообщение `Pose` и сохраняет его в
`latest_pose`. Callback таймера вызывает чистую функцию выбора команды и
публикует результат в `cmd_vel`.
`Ctrl+C` прерывает работу `spin`, после чего нода уничтожается и ROS-контекст
завершается. Прекращение процесса не является отдельной нулевой командой,
поэтому после остановки `patrol` нужно дождаться, пока turtlesim остановится.

# Исправление
```bash
ros2 run patrol patrol --ros-args \
  -r cmd_vel:=/turtle1/cmd_vel
```
С помощью remap относительное имя `cmd_vel` заменяется полным именем
`/turtle1/cmd_vel` без изменения Python-кода.

# Тест после исправления
Терминал B
```bash
ros2 run patrol patrol --ros-args \
  -r cmd_vel:=/turtle1/cmd_vel
```

Терминал C
Команда:
```bash
ros2 node info /patrol
```
Вывод:
```text
/patrol
  Subscribers:
    /turtle1/pose: turtlesim/msg/Pose
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Service Servers:
    /patrol/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /patrol/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /patrol/get_parameters: rcl_interfaces/srv/GetParameters
    /patrol/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /patrol/list_parameters: rcl_interfaces/srv/ListParameters
    /patrol/set_parameters: rcl_interfaces/srv/SetParameters
    /patrol/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:

  Action Clients:
```

Команда:
```bash
ros2 topic info /turtle1/cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: patrol
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.eb.7d.a1.89.9c.a4.00.00.00.00.00.00.14.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.eb.7d.d3.84.e8.ef.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

# Частота
```bash
ros2 topic hz /turtle1/cmd_vel
```
Вывод:
```text
average rate: 9.999
        min: 0.099s max: 0.101s std dev: 0.00065s window: 12
average rate: 9.998
        min: 0.099s max: 0.101s std dev: 0.00062s window: 22
average rate: 9.999
        min: 0.099s max: 0.101s std dev: 0.00065s window: 33
average rate: 10.001
        min: 0.099s max: 0.101s std dev: 0.00064s window: 44
average rate: 9.999
        min: 0.099s max: 0.101s std dev: 0.00063s window: 54
average rate: 10.001
        min: 0.098s max: 0.101s std dev: 0.00068s window: 65
average rate: 10.000
        min: 0.098s max: 0.101s std dev: 0.00066s window: 76
average rate: 9.999
        min: 0.098s max: 0.101s std dev: 0.00066s window: 86
average rate: 10.000
        min: 0.098s max: 0.101s std dev: 0.00065s window: 97
average rate: 10.001
        min: 0.098s max: 0.101s std dev: 0.00063s window: 108
average rate: 10.000
        min: 0.098s max: 0.101s std dev: 0.00062s window: 118
average rate: 10.000
        min: 0.098s max: 0.101s std dev: 0.00062s window: 129
```
