## Запуск и проверка вручную

Во всех терминалах из корня workspace:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
```

В терминале A:

```bash
ros2 launch turtle_bringup sim.launch.py
```

В терминале B:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

В терминале C:

```bash
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol publish_hz 5.0
ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
```

Реальные команды и полный вывод: [commands-fixed.txt](commands-fixed.txt).
Измерено: до обновления 10.023 Гц, после установки 5.0 — 5.003 Гц,
после отклонения нуля — 5.000 Гц. `param get` после нуля и после -1.0
возвращает `Double value is: 5.0`; CLI сообщает причину отказа.
После обновления скоростей сообщение Twist содержит `linear.x=0.8`
и `angular.z=-0.4`.
Тесты отрицательных значений, NaN, бесконечности, границ и атомарного отказа:
[tests.txt](tests.txt). NaN проверяется напрямую в чистой функции, чтобы
проверка не зависела от разбора YAML в CLI.

## Воспроизведение дефекта

Ветка `pr04-frequency-defect`, коммит
`0b4fa6aa56dbcde812e8e475273562de29238022`, отключает только проверку частоты.
В основной ветке проверка сохранена. Сценарий извлекает дефектный файл через
`git show` во временную папку и запускает его отдельно; исходники основной
ветки не переключаются и не перезаписываются.

Одинаковая последовательность для обоих вариантов:

```bash
ros2 param set /patrol publish_hz 5.0
ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol publish_hz 0.0
```

Без проверки ноль проходит в `apply`: старый таймер удаляется, а вычисление
`1.0 / new_hz` вызывает `ZeroDivisionError`, после чего процесс ноды завершается.
Полный отказ: [commands-defect.txt](commands-defect.txt) и
[patrol-defect.txt](patrol-defect.txt). В исправленном варианте запрос отклоняется,
параметр остаётся 5.0, поток команд продолжается около 5 Гц.

## Сервис /clear и действие rotate_absolute

```bash
ros2 service type /clear
ros2 interface show std_srvs/srv/Empty
ros2 service call /clear std_srvs/srv/Empty '{}'
ros2 action list -t
ros2 interface show turtlesim/action/RotateAbsolute
ros2 action send_goal /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute '{theta: 1.57}' --feedback
```

Реальный вывод всех команд: [services-actions.txt](services-actions.txt).
В этой установке тип действия — `turtlesim/action/RotateAbsolute`; если
`ros2 action list -t` показывает другой пакет, использовать именно найденный тип.

`/clear` удаляет линии, которые черепаха нарисовала в окне. Он не возвращает
черепаху в центр и не меняет её ориентацию. В команде `service call` первое имя
указывает сервис, затем идёт тип интерфейса, затем YAML с полями запроса.
`Empty` не содержит полей запроса или ответа, поэтому передаётся `{}`;
вывод `interface show` содержит разделитель `---` между пустыми частями.
Обработчик выполняет очистку и возвращает пустой ответ.

Действие `rotate_absolute` поворачивает черепаху к заданной абсолютной
ориентации. `theta: 1.57` — примерно pi/2 радиан относительно положительного
направления оси X, а не команда повернуться ещё на 1.57 радиана от текущего угла.
Его интерфейс содержит три части, разделённые `---`: цель (`theta`), результат
(`delta`) и обратную связь (`remaining`). CLI отправляет цель, получает
подтверждение принятия, с `--feedback` показывает оставшийся угол и затем результат.

**Отличие в двух предложениях:** запрос сервиса `/clear` вызывает короткую
операцию и получает один ответ, без протокола промежуточной обратной связи
и отмены. Цель действия `/turtle1/rotate_absolute` описывает требуемую
ориентацию для выполнения во времени: действие поддерживает обратную связь,
итоговый результат и запрос отмены.