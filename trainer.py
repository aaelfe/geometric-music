import gymnasium
from game_env import BuilderEnvironment
from gymnasium.envs.registration import register
from stable_baselines3 import PPO

import os
import time

models_dir = 'models/PPO'
log_dir = 'logs'

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

register(
    id='BuilderEnv',
    entry_point=lambda: BuilderEnvironment(),
)

env = gymnasium.make('BuilderEnv')
env.reset()

model = PPO("MultiInputPolicy", env, verbose=1, tensorboard_log=log_dir)

TIMESTEPS = 10000

i = 0
while True:
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, log_interval=1, tb_log_name=f'PPO_4_{i}')
    model.save(models_dir + f'/model_4_{i}')
    print(f'Trained model {i}')
    i += 1

# episodes = 10

# for episode in range(episodes):
#     obs = env.reset()
#     done = False
#     while not done:
#         action = env.action_space.sample()
#         obs, reward, done, _, info = env.step(action)
