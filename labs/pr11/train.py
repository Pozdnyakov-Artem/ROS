#!/usr/bin/env python3
"""Обучение табличной Q-политики для дискретной полосы."""

import argparse
import json
import random
from pathlib import Path

from lane_env import ACTIONS, LANE_LIMIT, ROUTE_LENGTH, LaneEnv


def choose_action(scores, epsilon, rng):
    if rng.random() < epsilon:
        return rng.randrange(len(ACTIONS))
    return max(range(len(ACTIONS)), key=scores.__getitem__)


def update_q(current, reward, next_max, terminated):
    target = reward if terminated else reward + 0.95 * next_max
    return current + 0.20 * (target - current)


def train():
    table = [
        [[0.0 for _ in ACTIONS] for _ in range(2 * LANE_LIMIT + 1)]
        for _ in range(ROUTE_LENGTH)
    ]
    rng = random.Random(12)
    env = LaneEnv()
    for episode in range(2000):
        state, _ = env.reset(seed=episode)
        epsilon = max(0.05, 1 - episode / 1200)
        while True:
            offset, remaining = state
            scores = table[remaining - 1][offset + LANE_LIMIT]
            action = choose_action(scores, epsilon, rng)
            next_state, reward, terminated, truncated, _ = env.step(ACTIONS[action])
            if terminated:
                next_max = 0.0
            else:
                next_offset, next_remaining = next_state
                next_max = max(table[next_remaining - 1][next_offset + LANE_LIMIT])
            scores[action] = update_q(scores[action], reward, next_max, terminated)
            if terminated or truncated:
                break
            state = next_state
    return table


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    policy = {'schema_version': 1, 'q': train()}
    payload = json.dumps(policy, indent=2, allow_nan=False)
    args.output.write_text(payload + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
