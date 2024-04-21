import pygame
import pygame.gfxdraw
import pygame.midi
import threading
import sys
import audio
import math
import time
from ball import Ball
from bounce_platform import BouncePlatform
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, GREEN, FPS, CAMERA_CENTER, INITIAL_VELOCITY, INITIAL_X, INITIAL_Y

MIDI_NOTE_ON = pygame.USEREVENT + 1

class GameStateManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

    # this state will only run once, to set up builder
    def reset(self, filepath='music/twinkle-twinkle-little-star.mid'):
        self.ball = Ball(x=INITIAL_X, y=INITIAL_Y, radius=15, color=WHITE, outline_color=RED, velocity=INITIAL_VELOCITY, gravity=-0.3, restitution=0.8)

        self.frame_data = []
        self.fps_data = []

        # fall for a bit before starting
        self.initial_fall(length_of_time=0.5)
        self.global_event_queue = audio.create_global_event_queue(filepath)

        self.playback_controls = { 
            "pause": threading.Event(),  
            "stop": threading.Event(),
            "total_paused_duration": 0,
            "pause_start_time": None,
            "time_until_next": self.global_event_queue[0][0],
            "can_resume": True,
            "alert_color": GREEN
        }
        audio.init()
        #self.midi_thread = threading.Thread(target=audio.trigger_builder_events, args=(self.global_event_queue, filepath, MIDI_NOTE_ON, self.playback_controls))
        #self.midi_thread.start()
        self.platforms = []
        self.terminated = False
        self.completed = False
        self.need_action_flag = False
        self.start_time = time.time()
        audio.play("music/twinkle-twinkle-little-star-non-16.wav")

    def step(self, action):
        for event in pygame.event.get():  # This ensures that all events are processed
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit  # Ensure a clean exit
        
        if not self.global_event_queue:
            self.completed = True
            return

        if not self.playback_controls["pause"].is_set():
            self.frame_data.append((self.ball.x, self.ball.y))
            self.fps_data.append(self.clock.get_fps())

        self.screen.fill(BLACK)
        self.vertical_offset = self.ball.y - CAMERA_CENTER

        # Calculate elapsed time, account for pause duration
        current_time = time.time() - self.start_time - self.playback_controls["total_paused_duration"] 

        print(f"Current time: {current_time}, Start time: {self.start_time}, Total paused duration: {self.playback_controls['total_paused_duration']}")

        if self.global_event_queue[0][0] <= current_time or self.need_action_flag:
            if not self.playback_controls["pause"].is_set():
                audio.pause_playback(self.playback_controls)
                self.ball.pause()

                self.new_platform = BouncePlatform(self.ball, length=50, width=10)
                self.platforms.append(self.new_platform)

                # Get action mask
                self.action_mask = self.get_action_mask()
                
                # if action mask all 0s, then terminate
                if sum(self.action_mask) == 0:
                    self.terminated = True
                    return

            # Use mask
            # if action is 1 - pop and execute action/add to paused duration and resume
            # else continue
            if self.action_mask[int(action)] == 1:
                #print("Action taken: ", action)
                #print last 10 points on action path for debugging
                # path = self.action_paths[int(action)]
                # print(path)
                self.need_action_flag = False
                time_of_note, events = self.global_event_queue.pop(0)

                # Calculate elapsed time, account for pause duration
                current_time = time.time() - self.start_time - self.playback_controls["total_paused_duration"]  

                self.playback_controls["time_until_next"] = 0
                if self.global_event_queue:
                    self.playback_controls["time_until_next"] = self.global_event_queue[0][0] - current_time

                pygame.gfxdraw.aacircle(self.screen, int(self.action_paths[int(action)][-1][0]), int(self.action_paths[int(action)][-1][1] - self.vertical_offset), 15, GREEN)
                pygame.gfxdraw.filled_circle(self.screen, int(self.action_paths[int(action)][-1][0]), int(self.action_paths[int(action)][-1][1] - self.vertical_offset), 15, GREEN)
                time.sleep(2)

                audio.resume_playback(self.playback_controls)
                self.ball.resume()

                self.platforms[-1].angle = action
                self.platforms[-1].recompute_verticies(True, self.vertical_offset)

                self.ball.bounce_off_platform(self.platforms[-1])
            else:
                self.need_action_flag = True

       
        self.ball.update()
        self.ball.draw(self.screen, y_offset=self.vertical_offset)

        # if self.playback_controls["pause"].is_set():
        #     pygame.gfxdraw.aacircle(self.screen, int(self.action_paths[int(action)][-1][0]), int(self.action_paths[int(action)][-1][1] - self.vertical_offset), 15, GREEN)
        #     pygame.gfxdraw.filled_circle(self.screen, int(self.action_paths[int(action)][-1][0]), int(self.action_paths[int(action)][-1][1] - self.vertical_offset), 15, GREEN)

        for platform in self.platforms:
            platform.draw(self.screen, y_offset=self.vertical_offset)

        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        self.clock.tick(FPS)

        # Calculate and display the frame rate
        pygame.display.set_caption("FPS: {:.2f}".format(self.clock.get_fps()))

    def close(self):
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()

    def initial_fall(self, length_of_time):
        # fall for a bit before starting
        start_time = time.time()
        current_time = time.time()
        self.vertical_offset = self.ball.y - CAMERA_CENTER
        while(current_time - start_time < length_of_time):
            self.frame_data.append((self.ball.x, self.ball.y))
            self.fps_data.append(self.clock.get_fps())

            self.screen.fill(BLACK)
            self.ball.update()
            self.ball.draw(self.screen, y_offset=self.vertical_offset)

            self.vertical_offset = self.ball.y - CAMERA_CENTER
            current_time = time.time()

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(FPS)

    def get_action_mask(self):
        action_mask = []
        self.action_paths = []

        for i in range(0, 360):
            can_take_action = True

            # Convert the angle to degrees and update the platform's angle
            self.platforms[-1].angle = i
            self.platforms[-1].recompute_verticies(True, self.vertical_offset)

            # If there will still be another platform after this one, 
            # project the bounce path and check for collisions
            if len(self.global_event_queue) > 1:
                time_to_project = self.global_event_queue[1][0] - self.global_event_queue[0][0]
                
                # Now, project the bounce path based on the new angle
                self.ball.project_bounce_path(self.platforms[-1].angle, total_time=time_to_project)#total_time=self.playback_controls["time_until_next"])
                self.action_paths.append(self.ball.projected_path)

                # Check for collisions with the projected path
                for point in self.ball.projected_path:
                    x, y = int(point[0]), int(point[1] - self.vertical_offset)
                    for i, platform in enumerate(self.platforms[:-1]):
                        if platform.check_collision((x,y), self.ball.radius):
                            can_take_action = False
                            break
                    if x < 5 or x > SCREEN_WIDTH - 5:
                        can_take_action = False
                        break

            # Check all frames of ball position for collision with new platform's placement
            # recent_frames = self.frame_data[:-1]

            for frame in self.frame_data[:-1]:
                ball_x, ball_y = frame
                if self.platforms[-1].check_collision((ball_x, ball_y - self.vertical_offset), self.ball.radius):
                    can_take_action = False
                    break

            if can_take_action:
                action_mask.append(1)
            else:
                action_mask.append(0)

        return action_mask