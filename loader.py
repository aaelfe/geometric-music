import gymnasium
from game_env import BuilderEnvironment
from gymnasium.envs.registration import register
from stable_baselines3 import PPO

import os

models_dir = 'models/PPO'
model_path = f"{models_dir}/model_4.zip"

register(
    id='BuilderEnv',
    entry_point=lambda: BuilderEnvironment(),
)

env = gymnasium.make('BuilderEnv')
env.reset()

model = PPO.load(model_path, env=env, verbose=1)

episodes = 10

for episode in range(episodes):
    obs, _ = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, _, info = env.step(action)
    env.playback()
