# Адаптер одометрии ПР07

## Маршрут и владельцы

- Bridge: Gazebo `/model/course_ackermann/odometry` -> ROS `/vehicle/odom_gz`.
- Вход: `header.frame_id=course_ackermann/odom`, `child_frame_id=course_ackermann/base_link`.
- Адаптер `/simulation/odom_adapter`: `/vehicle/odom_gz` -> `/vehicle/odom`.
- Выход: `header.frame_id=odom`, `child_frame_id=base_link`.
- Единственный владелец динамического ребра `odom -> base_link` - `odom_adapter`.
- Фиксированные ребра `base_link -> camera_link`, `base_link -> lidar_link`,
  `base_link -> imu_link` публикует `robot_state_publisher` из ПР06 в `/tf_static`.
- Bridge не публикует TF; Gazebo-топик `/model/course_ackermann/tf` не мостится.
- Наличие издателя `/tf` у robot_state_publisher не означает второго владельца
  `odom -> base_link`: он обслуживает дерево описания робота, без ребра odom.

## Что сохраняется

Нормализация меняет только две строки frames. Stamp, pose, twist и обе covariance
копируются без изменения. TF получает тот же stamp и ту же pose. Исходное
сообщение не изменяется. Другие frames и NaN/inf в pose, twist или covariance
отклоняются без публикации. Топики настраиваются параметрами input_topic и
output_topic. Нода работает с use_sim_time=true.

## Проверка модульными тестами

Команды выполнены в Bash существующего контейнера practical_hofstadter,
каталог /workspaces/ros, ROS 2 Jazzy:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
colcon test --packages-select course_description course_simulation --event-handlers console_direct+
colcon test-result --verbose
```

Результат: 47 тестов course_simulation прошли, в том числе 22 проверки одометрии.
Тест `test_frames_stamp_pose_twist_covariance_and_input_unchanged` использует
stamp 12.345678901 и ненулевые pose/twist/covariance. Он проверяет точное равенство
исходного и выходного stamp, pose, twist и обеих covariance, совпадение pose TF
и неизменность входного сообщения. Отдельные тесты отклоняют чужие frames и
NaN/inf во всех группах данных.

## Проверка работающих нод

На исправном headless-запуске сопоставлены сообщения с одинаковым stamp на
`/vehicle/odom_gz`, `/vehicle/odom`, `/tf`. Для 692
совпавших меток подтверждены сохранение pose, twist, обеих covariance и stamp,
а также совпадение TF с нормализованной одометрией. ros2 topic info -v показывает
ровно одного издателя нормализованного /vehicle/odom: /simulation/odom_adapter,
QoS reliable. В /drive/safe подписан только /simulation/drive_adapter.

Команда просмотра TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link --ros-args -p use_sim_time:=true
```

Фактический вывод сохранён в headless.txt. Статические связи датчиков получены
поздним подписчиком с transient_local. В MCAP найдено
1504 совпавших сообщений одометрии и TF; stamp и pose
совпали точно, frames нормализованы, все три фиксированных ребра сохранены.

## Запись

Локальная запись fixtures/pr07-sensors, MCAP, длительность 30.785 с
симуляционного времени. В ней все семь обязательных топиков непустые.
Исходная одометрия /vehicle/odom_gz в bag не включена: для ПР08 используется
уже нормализованный /vehicle/odom и записанные TF. Повторно запускать адаптер
при replay этого bag не нужно.
