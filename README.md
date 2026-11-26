## Практическая работа ПР12

Скрипт запускает проверку среды CarRacing-v2, обучает PPO на CPU в течение 4096 шагов с seed 17 и оценивает сохранённые веса на десяти отдельных трассах. Для оценки политика выбирает действия детерминированно.

Для установки нужны Linux x86-64, Python 3.12 и course kit `v1-w12`, распакованный в `.course-kit/`. Путь вывода должен указывать на новый каталог. Храните веса и каталог карточки вне рабочего дерева.

```bash
uv venv --python 3.12 .venv-pr12
source .venv-pr12/bin/activate
uv pip install -r .course-kit/v1/rl_carracing/requirements.txt
pr12_run="$(mktemp -d)/run"
bash labs/pr12/run.sh "$pr12_run"
hub_dir="$(mktemp -d)/model"
python -B .course-kit/v1/rl_carracing/prepare_hub.py \
  --run-dir "$pr12_run" --output "$hub_dir"
```

Журнал обучения, результаты всех заездов, карточка и разбор находятся в [evidence/pr12](evidence/pr12). Для публикации загрузите подготовленный каталог целиком согласно [условию ПР12](https://ros.lms.ci.nsu.ru/practices/pr12).

## Практическая работа ПР11

Табличная Q-политика учится удерживать робота в дискретной полосе. Она обучается на seed 0–1999 и проверяется на десяти отдельных seed из комплекта курса. Тесты проверяют обновление Q при завершении задачи и при достижении лимита шагов.

Нужен Python 3.10 или новее. Распакуйте course kit `v1-w12` в `.course-kit/`. В этой версии сохранена среда ПР11 и обновлён манифест сдачи.

```bash
mkdir -p evidence/pr11
PYTHONPATH=.course-kit/v1/rl_intro python3 -B -m unittest discover -s labs/pr11/tests -v
PYTHONPATH=.course-kit/v1/rl_intro python3 -B labs/pr11/train.py \
  --output evidence/pr11/q-table.json
python3 -B .course-kit/v1/rl_intro/evaluate.py \
  --policy evidence/pr11/q-table.json --output evidence/pr11/evaluation.json
```

Итоги заездов и разбор двух трасс с одинаковым seed сохранены в [evidence/pr11](evidence/pr11).

## Практическая работа ПР10

Выполнил: Колосов Егор. Docker `osrf/ros:jazzy-desktop-full` + `python3-jsonschema`, ROS 2 Jazzy, course kit `v1-w11`.

Пакеты `robotics_course_interfaces` (сообщение `SceneDescription` из course kit) и `scene_adapter`:
адаптер VLM публикует контракт SceneDescription v1 на `/perception/scene` в режимах mock и cache,
live — только с явно внедрённым backend. Копии схемы и fixtures лежат в `contracts/` и `fixtures/vlm/`,
их происхождение и SHA-256 — в [src/scene_adapter/README.md](src/scene_adapter/README.md),
параметры — `config/vlm.yaml`. Обязательные проверки offline, без API и сети.

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-up-to scene_adapter
source install/setup.bash
colcon test --packages-select scene_adapter --event-handlers console_direct+
colcon test-result --verbose
ros2 interface show robotics_course_interfaces/msg/SceneDescription
ros2 run scene_adapter scene_adapter --ros-args --params-file config/vlm.yaml
python3 .course-kit/v1/tools/check_practice.py PR10 --submission .
```

## Практическая работа ПР09

Выполнил: Колосов Егор. Docker `osrf/ros:jazzy-desktop-full`, ROS 2 Jazzy, course kit `v1-w11`.

Пакет `perception_baseline` — ROS-обёртка baseline-детектора из `.course-kit/v1/fixtures/pr09`:
2D-детекции, точка в `camera_optical_frame` по совмещённой глубине и диагностика причины,
если пространственный результат неизвестен. Запуск ноды и отправка тестовой пары:
[src/perception_baseline/README.md](src/perception_baseline/README.md).

Разбиение по `capture_id` (из корня репозитория):

```bash
mkdir -p data evidence/pr09
cp .course-kit/v1/fixtures/pr09/manifest-leaky.json data/manifest.json
python3 .course-kit/v1/tools/evaluate_perception.py \
  --fixture .course-kit/v1/fixtures/pr09 \
  --manifest data/manifest.json --allow-leak \
  --output evidence/pr09/metrics-before.json
# в data/manifest.json: calibration = sample-01..04 (capture-a, capture-b), test = sample-05, sample-06
python3 .course-kit/v1/tools/evaluate_perception.py \
  --fixture .course-kit/v1/fixtures/pr09 \
  --manifest data/manifest.json \
  --output evidence/pr09/metrics.json
```

Сборка и тесты:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select perception_baseline
source install/setup.bash
colcon test --packages-select perception_baseline --event-handlers console_direct+
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR09 --submission .
```

## Практическая работа ПР08

Пакет `localization_case` запускает карту, AMCL и lifecycle manager
на записи датчиков ПР07. Реализован измеритель доступности `map -> odom`
и ковариации по времени `/clock`, сохранены опыты с `chassis` и `base_link`.
Работа выполнена в существующем контейнере `practical_hofstadter`, ROS 2 Jazzy.

Подробное объяснение цели, всех компонентов, параметров, изменений,
экспериментов и команд: [evidence/pr08/README.md](evidence/pr08/README.md).
Результат: [localization.json](evidence/pr08/localization.json),
доказательство дефекта: [tf.md](evidence/pr08/tf.md),
график: [localization.png](evidence/pr08/localization.png).

В Bash существующего контейнера из `/workspaces/ros`:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select localization_case
source install/setup.bash
colcon test --packages-select localization_case --event-handlers console_direct+
export ROS_DOMAIN_ID=169
python3 tools/pr08/run_experiments.py --rate 0.5
```

Перед replay остановить симуляцию ПР07. В `evidence/pr08/report.json` указан
SHA коммита реализации. Отчёт, результаты измерений и декларация ИИ
входят в следующий коммит.

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

## Практическая работа ПР07

Пакет `course_simulation` запускает мир `mcity-minimal.sdf`, одного робота,
мост `ros_gz`, описание из ПР06 и адаптеры команд и одометрии.
Ноды работают в `/simulation`, контрактные имена топиков сохранены.

### Сборка и проверки

В Bash контейнера, из корня workspace `/workspaces/ros`:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
colcon build --symlink-install --packages-up-to course_simulation
source install/setup.bash
colcon test --packages-select course_description course_simulation --event-handlers console_direct+
colcon test-result --verbose
gz sdf -k src/course_simulation/models/course_ackermann/model.sdf
```

### Запуск симуляции

Во всех терминалах подключить ROS и `install/setup.bash`, установить
одинаковые домен ROS и раздел Gazebo:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
export GZ_PARTITION=pr07
```

В первом терминале из корня workspace:

```bash
mkdir -p evidence/pr07 fixtures
export DISPLAY=
export GZ_SIM_RESOURCE_PATH="$PWD/src/course_simulation/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
ros2 launch course_simulation simulation.launch.py \
  world:=$PWD/src/course_simulation/worlds/mcity-minimal.sdf \
  bridge_config:=$PWD/src/course_simulation/config/bridge.yaml \
  headless:=true 2>&1 | tee evidence/pr07/headless.txt
```

Gazebo запускается без окна с `-s -r --headless-rendering`; камера и лидар
используют OGRE2/EGL. Мир уже содержит робота. Первый терминал оставить
работающим до завершения проверок, затем остановить через `Ctrl+C`.

### Проверка топиков и команды

Во втором терминале с тем же окружением:

```bash
ros2 topic echo /clock rosgraph_msgs/msg/Clock --once
ros2 topic info -v /vehicle/imu
ros2 topic hz /vehicle/scan
```

```bash
ros2 topic pub --use-sim-time -r 20 /drive/safe \
  ackermann_msgs/msg/AckermannDriveStamped \
  '{header: auto, drive: {speed: 0.1, steering_angle: 0.2}}'
```

Пока источник работает, проверить путь команды и ответ модели:

```bash
ros2 topic echo /vehicle/gz_cmd_vel --once
gz topic -i -t /model/course_ackermann/cmd_vel
timeout 3s gz topic -e -t /model/course_ackermann/cmd_vel
ros2 topic echo /vehicle/odom --once
ros2 run tf2_ros tf2_echo odom base_link --ros-args -p use_sim_time:=true
```

ROS и Gazebo получают `linear.x` около 0.1 м/с и `angular.z` около
0.02534 рад/с. Положение в одометрии меняется, TF показывает ту же позу.
Физическое движение корпуса и колёс проверяется через
`/world/mcity_minimal/dynamic_pose/info` командой `gz topic -e -t`.
После опыта остановить источник и передать нулевую команду:

```bash
ros2 topic pub --use-sim-time --once /drive/safe \
  ackermann_msgs/msg/AckermannDriveStamped \
  '{header: auto, drive: {speed: 0.0, steering_angle: 0.0}}'
```

### Дефект и результаты

В копии YAML исходный Gazebo-топик IMU заменён на `/vehicle/imu_typo`.
`ros2 topic info -v /vehicle/imu` показывает издателя, но
`timeout 5s ros2 topic echo /vehicle/imu --once` завершается с кодом 124.
Команды `gz topic -i/-e -t /vehicle/imu` подтверждают, что исходный сенсор
работает. После восстановления имени и перезапуска того же launch сообщения
приходят. Одновременно второй мост не запускается.

Адаптер команды ограничивает скорость и угол, переводит Ackermann в Twist;
устаревшая команда и NaN/inf дают ноль. Адаптер одометрии сохраняет stamp,
pose, twist и обе covariance, меняет frames на `odom/base_link` и публикует
единственный TF `odom -> base_link`. Статические связи публикует
`robot_state_publisher` из ПР06.

Частота камеры изменена с 20 до 10 Гц. Измеренные `ros2 topic hz` частоты:
камера 7.062 Гц, лидар 7.538 Гц, IMU 74.857 Гц, одометрия 37.414 Гц.
Симуляция с программным рендерингом идёт медленнее реального времени;
частоты, frames и пояснения сохранены в `evidence/pr07/sensors.json`.
Команды и вывод находятся в `headless.txt`, проверки одометрии - в
`odom-adapter.md`, фактическая среда - в `workstation.txt`.

### Запись и проверка evidence

При работающем исправном launch в третьем терминале:

```bash
ros2 bag record --storage mcap --use-sim-time -o fixtures/pr07-sensors \
  --topics /vehicle/camera/image_raw /vehicle/scan /vehicle/imu \
  /vehicle/odom /tf /tf_static /clock
```

Остановить recorder через `Ctrl+C` после записи не менее 30 секунд
симуляционного времени. Затем:

```bash
ros2 bag info fixtures/pr07-sensors | tee evidence/pr07/bag-info.txt
python3 .course-kit/v1/tools/check_practice.py PR07 --submission .
```
