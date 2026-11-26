#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
  printf 'Usage: %s NEW_OUTPUT_DIRECTORY\n' "${0##*/}" >&2
  exit 2
fi

workspace="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
racing="$workspace/.course-kit/v1/rl_carracing/racing.py"
pr12_run="$1"

mkdir -- "$pr12_run"
python -B "$racing" check
python -B "$racing" train --steps 4096 --seed 17 --output "$pr12_run"
python -B "$racing" evaluate \
  --model "$pr12_run/policy.zip" --output "$pr12_run/evaluation.json"
