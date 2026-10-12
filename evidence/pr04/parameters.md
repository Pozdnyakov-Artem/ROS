# ПР04: параметры движения

Проверки выполнены в ROS 2 Jazzy, `ROS_DOMAIN_ID=116`.
В каждом терминале подключалось окружение:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=116
```

Запуск симулятора и ноды в отдельных терминалах:

```bash
ros2 run turtlesim turtlesim_node
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

## Допустимые значения и отказ без изменения состояния

Параметры по умолчанию: `publish_hz=10.0`, `linear_speed=0.5`, `turn_rate=0.3`.
Допустимы только конечные числа: частота 1–30 Гц, скорость 0–1 м/с,
поворот от -1 до 1 рад/с. Проверка выполняется до изменения активного состояния.
После принятой смены частоты старый таймер удаляется, период нового равен `1 / publish_hz`.

Ниже сохранён реальный вывод. Код 124 у `timeout ... topic hz` означает
окончание ограниченного по времени измерения. `ros2 param set` сообщает
об отказе текстом, хотя CLI возвращает код 0.

```text
$ ros2 param get /patrol publish_hz
Double value is: 10.0
[exit=0]

$ timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
WARNING: topic [/turtle1/cmd_vel] does not appear to be published yet
average rate: 10.134
	min: 0.085s max: 0.102s std dev: 0.00439s window: 11
average rate: 10.068
	min: 0.085s max: 0.102s std dev: 0.00318s window: 22
average rate: 10.046
	min: 0.085s max: 0.102s std dev: 0.00262s window: 33
average rate: 10.035
	min: 0.085s max: 0.102s std dev: 0.00231s window: 43
average rate: 10.013
	min: 0.085s max: 0.108s std dev: 0.00241s window: 53
average rate: 10.023
	min: 0.085s max: 0.108s std dev: 0.00242s window: 64
[exit=124]

$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
[exit=0]

$ timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
WARNING: topic [/turtle1/cmd_vel] does not appear to be published yet
average rate: 5.012
	min: 0.197s max: 0.200s std dev: 0.00119s window: 7
average rate: 5.007
	min: 0.197s max: 0.200s std dev: 0.00092s window: 13
average rate: 5.004
	min: 0.197s max: 0.201s std dev: 0.00083s window: 19
average rate: 5.003
	min: 0.197s max: 0.201s std dev: 0.00077s window: 24
average rate: 5.003
	min: 0.192s max: 0.209s std dev: 0.00229s window: 30
[exit=124]

$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz: значение должно быть от 1.0 до 30.0
[exit=0]

$ ros2 param get /patrol publish_hz
Double value is: 5.0
[exit=0]

$ timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
average rate: 5.002
	min: 0.199s max: 0.201s std dev: 0.00051s window: 7
average rate: 5.001
	min: 0.199s max: 0.201s std dev: 0.00054s window: 12
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00049s window: 18
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00045s window: 23
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00047s window: 29
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00047s window: 35
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00044s window: 41
[exit=124]

$ ros2 param set /patrol publish_hz -1.0
Setting parameter failed: publish_hz: значение должно быть от 1.0 до 30.0
[exit=0]

$ ros2 param get /patrol publish_hz
Double value is: 5.0
[exit=0]

$ ros2 param set /patrol linear_speed 0.8
Set parameter successful
[exit=0]

$ ros2 param set /patrol turn_rate -0.4
Set parameter successful
[exit=0]

$ ros2 topic echo /turtle1/cmd_vel --once
linear:
  x: 0.8
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: -0.4
---
[exit=0]
```

Итог: частота изменилась примерно с 10 на 5 Гц. Ноль и отрицательная частота
отклонены, значение 5.0 и поток сохранены. Изменение скоростей отразилось в Twist.

## Воспроизведение дефекта

В ветке `pr04-frequency-defect`, коммит
`0b4fa6aa56dbcde812e8e475273562de29238022`, временно отключена проверка частоты.
После установки 5.0 отправлена та же команда установки нуля, что в исправленной ноде.
Без проверки `apply` удаляет прежний таймер и вычисляет `1.0 / 0.0`;
исключение завершает процесс, клиент параметров остаётся без ответа.

```text
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
[exit=0]

$ timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
average rate: 5.001
	min: 0.200s max: 0.200s std dev: 0.00008s window: 7
average rate: 5.000
	min: 0.178s max: 0.221s std dev: 0.00876s window: 12
average rate: 4.999
	min: 0.178s max: 0.221s std dev: 0.00736s window: 17
average rate: 5.000
	min: 0.178s max: 0.221s std dev: 0.00634s window: 23
average rate: 5.000
	min: 0.178s max: 0.221s std dev: 0.00565s window: 29
average rate: 5.000
	min: 0.178s max: 0.221s std dev: 0.00514s window: 35
average rate: 5.000
	min: 0.178s max: 0.221s std dev: 0.00481s window: 40
average rate: 5.000
	min: 0.178s max: 0.221s std dev: 0.00454s window: 45
[exit=124]

$ timeout 15s ros2 param set /patrol publish_hz 0.0
[exit=124]
Defective node exited after publish_hz=0.0
Traceback (most recent call last):
  File "/tmp/tmp.1dvNwh5QmQ/patrol.py", line 129, in <module>
    main()
  File "/tmp/tmp.1dvNwh5QmQ/patrol.py", line 119, in main
    rclpy.spin(node)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/__init__.py", line 247, in spin
    executor.spin_once()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 926, in spin_once
    self._spin_once_impl(timeout_sec)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 918, in _spin_once_impl
    raise handler.exception()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/task.py", line 286, in _execute_coroutine_step
    result = coro.send(None)
             ^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 592, in handler
    await call_coroutine()
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 531, in _execute
    response = await await_or_execute(srv.callback, request, srv.srv_type.Response())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py", line 115, in await_or_execute
    return callback(*args)
           ^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/parameter_service.py", line 117, in _set_parameters_callback
    result = node.set_parameters_atomically([param])
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 839, in set_parameters_atomically
    return self._set_parameters_atomically(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 859, in _set_parameters_atomically
    return self._set_parameters_atomically_common(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 962, in _set_parameters_atomically_common
    self._call_post_set_parameters_callback(parameter_list)
  File "/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/node.py", line 1055, in _call_post_set_parameters_callback
    callback(parameter_list)
  File "/tmp/tmp.1dvNwh5QmQ/patrol.py", line 89, in apply
    1.0 / new_hz,
    ~~~~^~~~~~~~
ZeroDivisionError: float division by zero
```

В исправленном варианте эта команда отклонена, что видно в выводе выше.
Переход 10→5, ноль, отрицательная частота и NaN проверяются также тестами.
NaN передаётся непосредственно чистой функции `validate_values`, независимо
от разбора YAML в CLI. Результат `python3 -m pytest src/patrol/test`
сохранён в `tests.txt`.

## Сервис и действие

Реальные команды и вывод:

```text
$ ros2 service type /clear
std_srvs/srv/Empty
[exit=0]

$ ros2 interface show std_srvs/srv/Empty
---
[exit=0]

$ ros2 service call /clear std_srvs/srv/Empty \{\}
waiting for service to become available...
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()

[exit=0]

$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
[exit=0]
```

Запрос сервиса `/clear` выполняет очистку нарисованных линий и получает один
пустой ответ, без промежуточной обратной связи и протокола отмены.
Цель действия `/turtle1/rotate_absolute` задаёт требуемую ориентацию для выполнения
во времени: действие поддерживает обратную связь, итоговый результат и запрос отмены.
