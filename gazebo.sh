#!/usr/bin/env bash
set -e
source /opt/ros/jazzy/setup.bash
if [ "$#" -eq 0 ]; then
    set -- empty.sdf
fi
exec gz sim --render-engine ogre "$@"
