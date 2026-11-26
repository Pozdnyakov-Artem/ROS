---
library_name: stable-baselines3
tags:
- CarRacing-v2
- reinforcement-learning
- stable-baselines3
model-index:
- name: PPO
  results:
  - task:
      type: reinforcement-learning
      name: Reinforcement learning
    dataset:
      name: CarRacing-v2
      type: CarRacing-v2
    metrics:
    - type: mean_reward
      name: mean_reward
      value: "-64.957179 +/- 8.701663"
      verified: false
---

# PPO в CarRacing-v2

Политика с непрерывным управлением. Результаты получены при детерминированном
выборе действия на десяти заездах с seed 101, 202, 303, 404, 505, 606, 707, 808, 909, 1010.
Стандартное отклонение рассчитано по всем десяти заездам.

- `ppo-CarRacing-v2.zip` содержит веса оценивавшейся политики. SHA-256: `47693dca5d3caa062fb12668ac07526e8c47568adf14faab9540c6d27da15502`.
- `training.json` содержит параметры обучения.
- `evaluation.json` содержит результаты каждого заезда и сводные метрики.
- `requirements.txt` фиксирует версии библиотек.
