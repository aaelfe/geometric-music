import numpy as np
import pygame
import threading

import gymnasium as gym
from gymnasium import spaces

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GREEN, RED

import audio
from gym_state_manager import GameStateManager

MIDI_NOTE_ON = pygame.USEREVENT + 1

class BuilderEnvironment(gym.Env):
    def __init__(self):
        # This defines a single (x, y) coordinate space where x and y are integers within the screen dimensions
        coordinate_space = spaces.Box(low=np.array([0, 0]), high=np.array([SCREEN_WIDTH, SCREEN_HEIGHT]), dtype=float)

        # Observations are dictionaries with the agent's and the target's location.
        # Each location is encoded as an element of {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).
        self.observation_space = spaces.Dict(
            {
                "agent": spaces.Box(low=np.array([0,0]), high=np.array([SCREEN_WIDTH, SCREEN_HEIGHT]), dtype=float),
                "platforms": spaces.Box(low=np.zeros((25, 2), dtype=float),
                            high=np.array([[SCREEN_WIDTH, SCREEN_HEIGHT]]*25, dtype=float)),
                "velocity": spaces.Box(low=np.array([-50, -50]), high=np.array([50, 50]), dtype=float)
            }
        )
        # Action space is an angle in degrees
        self.action_space = spaces.Discrete(360)

        self.state_manager = GameStateManager()

    def reset(self, seed=None, options=None):
        # select midi file
        midi_filepath = "music/short-test.mid"
        wav_filepath = "music/short-test.wav"

        self.state_manager.reset(rate=1)

        observation = self._get_obs()
        info = self._get_info()

        return observation, info

    def step(self, action):
        self.state_manager.step(action)

        terminated = self.state_manager.terminated
        completed = self.state_manager.completed
        num_platforms = len(self.state_manager.platforms)
        vertical_offset = self.state_manager.vertical_offset

        reward = num_platforms - vertical_offset/10
        if terminated and completed:
            reward *= 2
        elif terminated:
            reward *= 0.5

        #reward = 10 if terminated and completed else -10 if terminated else 0
        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, False, info

    def close(self):
        self.state_manager.close()
        self.state_manager.midi_thread.join()

    def playback(self):
        self.state_manager.init_playback()

    def _get_obs(self):
        platform_locations = []

        # Collect platform locations
        for platform in self.state_manager.platforms:
            platform_locations.append(np.array([platform.x, platform.y], dtype=np.float32))
        
        # Ensure only the last 25 platform locations are kept if there are more than 25 platforms
        if len(platform_locations) > 25:
            platform_locations = platform_locations[-25:]
        elif len(platform_locations) < 25:
            # Pad with zeros if there are fewer than 25 platforms to maintain a fixed size (25, 2)
            platform_locations.extend([np.array([0, 0], dtype=np.float32)] * (25 - len(platform_locations)))

        # Convert list of platform locations to a numpy array
        platform_locations = np.array(platform_locations, dtype=np.float32)

        # Padding is no longer needed here because we have ensured the array is always (25, 2)
        return {
            "agent": np.array([self.state_manager.ball.x, self.state_manager.ball.y], dtype=np.float64),
            "platforms": platform_locations,  # This is a fixed-size array of shape (25, 2)
            "velocity": np.array([self.state_manager.ball.velocity[0], self.state_manager.ball.velocity[1]], dtype=np.float64)
        }
        # platform_locations = []

        # for platform in self.state_manager.platforms:
        #     platform_locations.append(np.array([platform.x, platform.y], dtype=np.float64))
        
        # while len(platform_locations) < len(self.state_manager.global_event_queue):
        #     platform_locations.append(np.array([0, 0], dtype=np.float64))

        # # create a platform_locations array that is properly shaped/formatted for observation space
        # platform_locations = np.array(platform_locations, dtype=np.float64)
        # platform_locations = np.pad(platform_locations, ((0, len(self.state_manager.global_event_queue) - len(platform_locations)), (0, 0)), mode='constant')

        # return {
        #     "agent": np.array([self.state_manager.ball.x, self.state_manager.ball.y], dtype=np.float64),
        #     "platforms": platform_locations  # This is a list of ndarrays now
        # }
    
    # filler for now, don't know what info will consist of
    def _get_info(self):
        return {
            # "distance": np.linalg.norm(
            #     self._agent_location - self._target_location, ord=1
            # )
        }