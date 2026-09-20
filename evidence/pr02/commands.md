# Команды Linux
`cat .gitignore` - выводит содержимое файлов в терминал и позволяет объединять несколько файлов.
Выовд:
```text
.course-kit/
robotics-course-kit-*.tar.gz
robotics-course-kit-*.sha256.txt
build
install
```
`ls -a evidence` - показывает все файлы и каталоги в текущем каталоге, включая скрытые.
Вывод:
```text
.  ..  pr01  pr02
```
`pwd` - выводит полный путь текущего каталога, с помощью неё проверяю, что терминал
находится в корне workspace.
```text
/workspaces/ros
```

# Отличие > от |
`>` - перенаправляет вывод команды в файл и заменяет прежнее содержимое
`|` - передаёт вывод одной команды на стандартный ввод следующей
команды
# Отличие source от запуска программы
Команда `source` выполняет содержимое файла в текущей оболочке. Поэтому изменения переменных окружения остаются в текущем терминале. При обычном запуске новой программы создаётся отдельный процесс. Изменения переменных внутри дочернего процесса не могут изменить окружение родительской оболочки.

# Запуск и остановка launch-файла
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
```
Путь установленного пакета был проверен командой:
```bash
ros2 pkg prefix turtle_bringup
```
Вывод:
```text
/workspaces/ros/install/turtle_bringup
```
Пакет был запущен через установленный launch-файл:
```bash
ros2 launch turtle_bringup sim.launch.py
```
После запуска открылось одно окно turtlesim. В другом терминале с тем же
`ROS_DOMAIN_ID` была выполнена проверка графа:
```bash
ros2 node list --no-daemon --spin-time 2
```
Вывод:
```text
/turtlesim
```
Launch был остановлен сочетанием `Ctrl+C`. Вместе с ним закрылось окно
turtlesim, а нода `/turtlesim` исчезла из графа. Затем launch был повторно
запущен для проверки доставки команд движения.

# Управление черепахой через терминал
## Команда:
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
Показывает структуру сообщения geometry_msgs/msg/Twist, какие поля и какие типы данных
## Команда:
```bash
ros2 topic type /turtle1/pose
```
Вывод:
```text
turtlesim/msg/Pose
```
Показывает структуру сообщения, передаваемого через топик /turtle1/pose
## Команда:
```bash
ros2 topic echo /turtle1/pose --once
```
Вывод:
```yaml
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```
Показывает координаты черепахи
## Команда:
```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
Вывод:
```text
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```
От временного издателя отправляет один раз для топика `/turtle1/cmd_vel` сообщение типа `geometry_msgs/msg/Twist`, в котором указывается направление движения
## Команда:
```bash
ros2 topic echo /turtle1/pose --once
```
Вывод:
```yaml
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
---
```
## Ожидания
Ожидал что черепаха сдвинется вперёд и влево, точных координат не ожидал, потому что задаём движение по дуге. 

# Сравнение «до / сбой / после»
## Сбой
Команда:
```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
Вывод:
```text
Много раз такое:
publishing #4: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```
Команда:
```bash
ros2 topic info /cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_11182
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.eb.7d.ae.2b.ab.36.00.00.00.00.00.00.07.03
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
Команда:
```bash
ros2 topic info /turtle1/cmd_vel --verbose
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
GID: 01.0f.eb.7d.1b.26.38.82.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```
## После
Команда:
```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
Вывод:
```text
Много раз такое:
publishing #4: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```
Команда:
```bash
ros2 topic info /cmd_vel --verbose
```
Вывод:
```text
Unknown topic '/cmd_vel'
```
Команда:
```bash
ros2 topic info /turtle1/cmd_vel --verbose
```
Вывод:
```text
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_12109
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.eb.7d.4d.2f.09.81.00.00.00.00.00.00.07.03
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
GID: 01.0f.eb.7d.1b.26.38.82.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```
## Отличия
При сбое для топика `/cmd_vel` был только издатель, а для топика `/turtle1/cmd_vel` был только подписчик и не было издателя. После исправление для топика `/turtle1/cmd_vel` был и подписчик и издатель, поэтому команды доходили, а топик `/cmd_vel` пропал так как не использовался.
## Вывод
Правильного типа сообщения недостаточно. Для обмена издатель и подписчик должны находиться в одном ROS-домене, использовать одно и то же полное имя топика и совместимый тип сообщения. В опыте тип и домен были правильными, а причиной сбоя было различие имён `/cmd_vel` и `/turtle1/cmd_vel`.
