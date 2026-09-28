#!/usr/bin/env bash
# Run from the workspace root in a ROS 2 Jazzy container.
set -eo pipefail
source /opt/ros/jazzy/setup.bash
source install/setup.bash
set -u
export ROS_DOMAIN_ID=116
export ROS2CLI_NO_DAEMON=1
export PYTHONUNBUFFERED=1
mkdir -p evidence/pr04
task_tmp=$(mktemp -d)
sim_pid=''
patrol_pid=''
cleanup() {
    for pid in "$patrol_pid" "$sim_pid"; do
        if [ -n "$pid" ]; then
            kill -TERM -- "-$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done
    rm -rf -- "$task_tmp"
}
trap cleanup EXIT
run() {
    printf '\n$'
    printf ' %q' "$@"
    printf '\n'
    local code=0
    "$@" || code=$?
    printf '[exit=%s]\n' "$code"
    if [ "$code" -ne 0 ] && [ "$code" -ne 124 ]; then
        return "$code"
    fi
}
wait_patrol() {
    for attempt in $(seq 1 6); do
        if timeout 15s ros2 param get /patrol publish_hz > /dev/null 2>&1; then
            return 0
        fi
        sleep 0.2
    done
    return 1
}
stop_patrol() {
    kill -TERM -- "-$patrol_pid" 2>/dev/null || true
    wait "$patrol_pid" 2>/dev/null || true
    patrol_pid=''
}

# Offscreen rendering allows this experiment to run without opening a window.
QT_QPA_PLATFORM=offscreen setsid ros2 run turtlesim turtlesim_node \
    > evidence/pr04/simulator.txt 2>&1 &
sim_pid=$!
setsid ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel \
    > evidence/pr04/patrol-fixed.txt 2>&1 &
patrol_pid=$!
wait_patrol
{
    run ros2 param get /patrol publish_hz
    run timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
    run ros2 param set /patrol publish_hz 5.0
    run timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
    run ros2 param set /patrol publish_hz 0.0
    run ros2 param get /patrol publish_hz
    run timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
    run ros2 param set /patrol publish_hz -1.0
    run ros2 param get /patrol publish_hz
    run ros2 param set /patrol linear_speed 0.8
    run ros2 param set /patrol turn_rate -0.4
    run ros2 topic echo /turtle1/cmd_vel --once
} > evidence/pr04/commands-fixed.txt 2>&1
stop_patrol

{
    run ros2 service type /clear
    run ros2 interface show std_srvs/srv/Empty
    run ros2 service call /clear std_srvs/srv/Empty '{}'
    run ros2 action list -t
    run ros2 interface show turtlesim/action/RotateAbsolute
    run ros2 action send_goal /turtle1/rotate_absolute \
        turtlesim/action/RotateAbsolute '{theta: 1.57}' --feedback
} > evidence/pr04/services-actions.txt 2>&1

# The defect branch disables only frequency validation.
git show pr04-frequency-defect:src/patrol/patrol/patrol.py \
    > "$task_tmp/patrol.py"
setsid python3 "$task_tmp/patrol.py" --ros-args -r cmd_vel:=/turtle1/cmd_vel \
    > evidence/pr04/patrol-defect.txt 2>&1 &
patrol_pid=$!
wait_patrol
{
    run ros2 param set /patrol publish_hz 5.0
    run timeout --signal=INT 15s ros2 topic hz /turtle1/cmd_vel
    run timeout 15s ros2 param set /patrol publish_hz 0.0
    sleep 1
    if kill -0 "$patrol_pid" 2>/dev/null; then
        printf 'ERROR: defective node unexpectedly survived\n'
        exit 1
    fi
    printf 'Defective node exited after publish_hz=0.0\n'
    cat evidence/pr04/patrol-defect.txt
} > evidence/pr04/commands-defect.txt 2>&1
stop_patrol
printf 'Experiments completed; logs saved in evidence/pr04/\n'
