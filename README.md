## Практическая работа ПР01

Работа выполнялась в ROS 2 Jazzy. Для опыта использовались домены 16 и 17.

Во всех терминалах сначала подключается окружение ROS:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
```

### Запуск исправного графа

Терминал A - симулятор:

```bash
ros2 run turtlesim turtlesim_node
```

Терминал B - управление с клавиатуры:

```bash
ros2 run turtlesim turtle_teleop_key
```

Терминал C - наблюдение:

```bash
mkdir -p evidence/pr01
ros2 doctor --report > evidence/pr01/doctor.txt 2>&1

ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose

POSE_TYPE=$(ros2 topic type /turtle1/pose)
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

### Разрыв связи

Симулятор продолжает работать в домене 16.

В терминале B нода управления останавливается через `Ctrl+C` и запускается
в домене 17:

```bash
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

В терминале C:

```bash
export ROS_DOMAIN_ID=17
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once \
  > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```

Результат: `exit=124`: за пять секунд поза не поступает.

### Восстановление связи

В терминале B нода управления снова останавливается и запускается в домене 16:

```bash
export ROS_DOMAIN_ID=16
ros2 run turtlesim turtle_teleop_key
```

В терминале C:

```bash
export ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once \
  > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?"
```

Результат: получение позы и `exit=0`.

### Проверка evidence

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```

## Практическая работа ПР02
Пакет `turtle_bringup` содержит launch-файл для запуска готовой ноды
`turtlesim_node`. Работа выполняется в ROS 2 Jazzy с доменом 16.
### Сборка пакета
Из корня workspace:
```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
colcon build --symlink-install --packages-select turtle_bringup
```
### Запуск через launch-файл
В новом терминале из корня workspace:
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 pkg prefix turtle_bringup
ros2 launch turtle_bringup sim.launch.py
```
После запуска открывается окно turtlesim и в графе появляется нода
`/turtlesim`. Запуск останавливается сочетанием `Ctrl+C`; вместе с launch
завершается запущенная им нода turtlesim.
### Проверка графа и отправка команды
В другом терминале с тем же окружением и доменом:
```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
Команда задаёт движение вперёд по дуге против часовой стрелки.
### Воспроизведение ошибки имени топика
Ошибочный издатель запускается в топике `/cmd_vel`, на который нода
`/turtlesim` не подписана:
```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
После остановки издателя через `Ctrl+C` исправляется только полное имя топика:
```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```
### Локальная проверка
```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

## Практическая работа ПР03

Пакет `patrol` содержит ноду, которая подписывается на `/turtle1/pose` и
публикует команды `geometry_msgs/msg/Twist` с периодом 0,1 секунды.

### Сборка и тесты

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
python3 -m pytest src/patrol/test
```

### Запуск без remap

```bash
ros2 run patrol patrol
```

Относительное имя `cmd_vel` разрешается в `/cmd_vel`, поэтому издатель не
соединяется с подписчиком turtlesim в `/turtle1/cmd_vel`.

### Запуск с remap

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Remap связывает издателя patrol с подписчиком turtlesim без изменения кода
ноды. Ожидаемая частота публикации команды — около 10 Гц.

### Проверка evidence

```bash
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

## Практическая работа ПР05

Пакет `course_bringup` запускает глобальный turtlesim, ноду `patrol`,
ретранслятор положения и подписчик с настраиваемым QoS. Ноды управления
и проверки работают в пространстве имён `/robot_a`. Команды скорости
переназначены в `/turtle1/cmd_vel`, а сенсорный поток публикуется
в `/robot_a/sensor_pose` с `best_effort`.

### Сборка и тесты

Из корня рабочего пространства в контейнере ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol course_bringup
source install/setup.bash
colcon test --packages-select turtle_bringup patrol course_bringup --event-handlers console_direct+
colcon test-result --verbose
```

### Запуск опыта

Во всех терминалах подключите ROS и `install/setup.bash` и установите
одинаковый `ROS_DOMAIN_ID`. Для несовместимого подписчика:

```bash
export ROS_DOMAIN_ID=16
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=reliable record:=false
```

После остановки первого запуска исправленный вариант с записью:

```bash
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort \
  record:=true bag_dir:=evidence/pr05/bag
```

Каталог записи должен быть свободен. Существующий `evidence/pr05/bag`
содержит исходный опыт; для новой записи выберите другой путь.

### Повтор исходной записи

Остановите живой launch и выполните:

```bash
ros2 bag play evidence/pr05/bag \
  --qos-profile-overrides-path config/qos-overrides.yaml --loop
```

В другом терминале с тем же окружением и доменом:

```bash
timeout 15s ros2 topic echo /robot_a/sensor_pose turtlesim/msg/Pose \
  --qos-reliability reliable --once
timeout 15s ros2 topic echo /robot_a/sensor_pose turtlesim/msg/Pose \
  --qos-reliability best_effort --once
```

Первый подписчик завершается по тайм-ауту с кодом 124. Второй получает
сообщение и завершается с кодом 0. Тот же результат проверен на живом
потоке и собственным `pose_subscriber`. Подробности, результаты и порядок
завершения сдачи находятся в `evidence/pr05/README.md`.

CI использует фиксированную ревизию course kit `v1-w05`, собирает и
тестирует три пакета, затем проверяет отчёт PR05. Поле `commit` в отчёте
нужно заполнить SHA коммита реализации перед окончательной проверкой.

## Практическая работа ПР06

Пакет `course_description` описывает корпус Ackermann-робота, четыре
колеса, два поворотных звена, камеру, лидар и IMU. Колёсная база — 0,8 м,
колея — 0,62 м, радиус колеса — 0,12 м. Размеры взяты из SDF course kit;
исходный SDF не изменён. Связи модели публикует один `robot_state_publisher`.

### Сборка и проверки

В Bash внутри ROS 2 Jazzy контейнера, из корня workspace:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select course_description
source install/setup.bash
xacro src/course_description/urdf/vehicle.urdf.xacro > /tmp/vehicle.urdf
check_urdf /tmp/vehicle.urdf
colcon test --packages-select course_description --event-handlers console_direct+
colcon test-result --verbose
```

### Просмотр и положения колёс

Во всех терминалах подключить ROS и `install/setup.bash`, установить
одинаковый домен; повторная проверка выполнялась в `ROS_DOMAIN_ID=16`.

```bash
export ROS_DOMAIN_ID=16
ros2 launch course_description display.launch.py
```

В RViz используется `Fixed Frame=base_link`. Камера, лидар и IMU
публикуются в `/tf_static` сразу. Положения подвижных звеньев появляются
в `/tf` после поступления `/joint_states`. Для их отображения во втором
терминале с тем же окружением и доменом:

```bash
ros2 topic pub -r 10 /joint_states sensor_msgs/msg/JointState \
  '{header: auto, name: [front_left_steering_joint, front_right_steering_joint, front_left_wheel_joint, front_right_wheel_joint, rear_left_wheel_joint, rear_right_wheel_joint], position: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}'
```

Для запуска без окна используется `rviz:=false`. Перед повторным запуском
остановить прежний launch, чтобы не получить двух издателей преобразований.

### Дефект и результаты

В коммите `1823921` родитель `lidar_link` изменён с `base_link` на
`camera_link` при прежнем смещении `(0.28, 0, 0.38)`. Положение лидара
относительно корпуса стало `(0.56, 0, 0.76)`. `check_urdf` принимает такое
дерево, но неизменённый тест родителя лидара падает. В рабочей модели
родитель восстановлен: тест проходит, координаты снова `(0.28, 0, 0.38)`.

`evidence/pr06/model-check.txt` содержит команды и результаты до/после,
`frames.md` — таблицу связей и владельцев. В `tf-qos.txt` поздний подписчик
`reliable/transient_local` получает историю `/tf_static` с кодом 0,
а `reliable/volatile` завершается без сообщений по тайм-ауту с кодом 124.

Для ПР06 локально и в CI используется фиксированный course kit `v1-w07`.
После создания коммита окончательной реализации его полный SHA записывается
в `evidence/pr06/report.json`, затем отчёт и `AI_USAGE.md` сохраняются
отдельным коммитом. Перед сдачей:

```bash
python3 .course-kit/v1/tools/check_practice.py PR06 --submission .
```
