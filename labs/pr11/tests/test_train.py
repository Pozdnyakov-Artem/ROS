import random
import unittest

from lane_env import MAX_STEPS, LaneEnv

from labs.pr11.train import choose_action, update_q


class QLearningTests(unittest.TestCase):
    def test_terminated_does_not_bootstrap(self):
        self.assertAlmostEqual(update_q(1.0, 2.0, 4.0, terminated=True), 1.20)

    def test_time_limit_bootstraps(self):
        env = LaneEnv()
        env.reset(seed=12)
        for _ in range(MAX_STEPS):
            _, _, terminated, truncated, _ = env.step('stop')
        self.assertFalse(terminated)
        self.assertTrue(truncated)
        self.assertAlmostEqual(update_q(1.0, 2.0, 4.0, terminated), 1.96)

    def test_greedy_tie_uses_first_action(self):
        self.assertEqual(choose_action([4.0, 4.0, 1.0, 0.0], 0.0, random.Random(12)), 0)


if __name__ == '__main__':
    unittest.main()
