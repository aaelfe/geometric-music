# import gymnasium
# from game_env import BuilderEnvironment
# from gymnasium.envs.registration import register

# register(
#     id='MyCustomEnv-v0',
#     entry_point=lambda: BuilderEnvironment(midi_file_path='twinkle-twinkle-little-star.mid'),
# )

# env = gymnasium.make('MyCustomEnv-v0')




# from stable_baselines3.common.env_checker import check_env
# from game_env import BuilderEnvironment


# env = BuilderEnvironment()
# # It will check your custom environment and output additional warnings if needed
# check_env(env)




from game_env import BuilderEnvironment


env = BuilderEnvironment()
episodes = 50

for episode in range(episodes):
	done = False
	obs = env.reset()
	while not done:
		random_action = env.action_space.sample()
		#print("action",random_action)
		obs, reward, done, trunc, info = env.step(random_action)
		#print('reward',reward)