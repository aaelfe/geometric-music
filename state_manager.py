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
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, FPS, CAMERA_CENTER, INITIAL_VELOCITY, INITIAL_X, INITIAL_Y

MIDI_NOTE_ON = pygame.USEREVENT + 1

class GameStateManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MAIN_MENU"

        self.ball = Ball(x=INITIAL_X, y=INITIAL_Y, radius=15, color=WHITE, outline_color=RED, velocity=INITIAL_VELOCITY, gravity=-0.1, restitution=0.8)

    def main_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Example of switching to the game state
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = "INIT_BUILDER"
        self.screen.fill((0, 100, 200))
        # Render main menu...
        pygame.display.flip()

    # this state will only run once, to set up builder
    def init_builder(self):
        # fall for a bit before starting
        self.initial_fall(length_of_time=0.5)

        self.playback_controls = { 
            "pause": threading.Event(),  
            "stop": threading.Event(),
            "total_paused_duration": 0,
            "pause_start_time": None,
            "time_until_next": 0
        }
        audio.init()
        audio.play_wav("music/twinkle-twinkle-little-star-non-16.wav")
        global_event_queue = audio.create_global_event_queue('music/twinkle-twinkle-little-star.mid')
        self.midi_thread = threading.Thread(target=audio.trigger_builder_events, args=(global_event_queue, MIDI_NOTE_ON, self.playback_controls))
        self.midi_thread.start()
        self.platforms = []
        self.frame_data = []
        self.state = "BUILDER"

    def builder(self):
        if not self.playback_controls["pause"].is_set():
           self.frame_data.append((self.ball.x, self.ball.y))

        self.screen.fill(BLACK)
        self.vertical_offset = self.ball.y - CAMERA_CENTER

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == MIDI_NOTE_ON:
                # Handle the MIDI note on event
                audio.pause_playback(self.playback_controls)
                self.ball.pause()

                new_platform = BouncePlatform(self.ball, length=50, width=10)
                self.platforms.append(new_platform)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                audio.resume_playback(self.playback_controls)
                self.ball.resume()
                self.ball.bounce_off_platform(self.platforms[-1])

            # event during pauses
            elif event.type == pygame.MOUSEMOTION and self.playback_controls["pause"].is_set():
                # Calculate the new angle for the platform based on mouse position
                mouse_x, mouse_y = event.pos
                # Calculate the angle in radians between the mouse and the ball's center
                angle_rad = math.atan2(self.ball.y - mouse_y - self.vertical_offset, mouse_x - self.ball.x)
                # Convert the angle to degrees and update the platform's angle
                self.platforms[-1].angle = math.degrees(angle_rad) % 360

                # Now, project the bounce path based on the new angle
                self.ball.project_bounce_path(self.platforms[-1].angle, total_time=self.playback_controls["time_until_next"])
            
            elif self.playback_controls["stop"].is_set():
                self.midi_thread.join()
                self.state = "INIT_PLAYBACK"

            pygame.time.delay(10)  # Small delay to limit CPU usage
        
        self.ball.update()
        self.ball.draw(self.screen, y_offset=self.vertical_offset)

        for i, platform in enumerate(self.platforms):
            is_recent = (i == len(self.platforms) - 1)
            platform.draw(self.screen, y_offset=self.vertical_offset, is_recent=is_recent)
        
        if self.playback_controls["pause"].is_set():
            self.platforms[-1].draw(self.screen, y_offset=self.vertical_offset)

            # Draw the projected path (simplified example)
            for point in self.ball.projected_path:
                x, y = int(point[0]), int(point[1] - self.vertical_offset)
                # Draw the outline
                pygame.gfxdraw.aacircle(self.screen, x, y, 15, RED)
                pygame.gfxdraw.filled_circle(self.screen, x, y, 15, RED)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        self.clock.tick(FPS)

    # run once to set up playback
    def init_playback(self):
        # reset ball position and velocity
        self.ball.x = INITIAL_X
        self.ball.y = INITIAL_Y
        self.ball.velocity = INITIAL_VELOCITY

        # replay initial fall
        self.initial_fall(length_of_time=0.5)

        self.playback_controls = { 
            "pause": threading.Event(),  
            "stop": threading.Event(),
            "total_paused_duration": 0,
            "pause_start_time": None,
            "time_until_next": 0
        }

        audio.init()
        audio.play_wav("music/twinkle-twinkle-little-star-non-16.wav")
        global_event_queue = audio.create_global_event_queue('music/twinkle-twinkle-little-star.mid')
        self.midi_thread = threading.Thread(target=audio.trigger_playback_events, args=(global_event_queue, MIDI_NOTE_ON, self.playback_controls))
        self.midi_thread.start()
        self.platform_index = 0

        self.state = "PLAYBACK"

    def playback(self):
        self.screen.fill(BLACK)
        vertical_offset = self.ball.y - CAMERA_CENTER

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # elif event.type == MIDI_NOTE_ON:
            #     self.ball.bounce_off_platform(self.platforms[self.platform_index])
            #     self.platform_index += 1

            elif self.playback_controls["stop"].is_set():
                self.midi_thread.join()
                self.state = "MAIN_MENU"

            pygame.time.delay(10)  # Small delay to limit CPU usage
        
        if(len(self.frame_data) > self.platform_index):
            self.ball.x = self.frame_data[self.platform_index][0]
            self.ball.y = self.frame_data[self.platform_index][1]
        self.platform_index += 1
        #self.ball.update()
        self.ball.draw(self.screen, y_offset=vertical_offset)

        for platform in self.platforms:
            platform.draw(self.screen, y_offset=vertical_offset)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        self.clock.tick(FPS)

    def initial_fall(self, length_of_time):
        # fall for a bit before starting
        start_time = time.time()
        current_time = time.time()
        self.vertical_offset = self.ball.y - CAMERA_CENTER
        while(current_time - start_time < length_of_time):
            self.screen.fill(BLACK)
            self.ball.update()
            self.ball.draw(self.screen, y_offset=self.vertical_offset)

            self.vertical_offset = self.ball.y - CAMERA_CENTER
            current_time = time.time()

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(FPS)

    def run(self):
        while self.running:
            if self.state == "MAIN_MENU":
                self.main_menu()
            elif self.state == "INIT_BUILDER":
                self.init_builder()
            elif self.state == "BUILDER":
                self.builder()
            elif self.state == "INIT_PLAYBACK":
                self.init_playback()
            elif self.state == "PLAYBACK":
                self.playback()
        pygame.quit()
        sys.exit()

game = GameStateManager()
game.run()