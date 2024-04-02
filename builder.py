import pygame
import pygame.midi
import threading
import sys
import audio
import math
from ball import Ball
from bounce_platform import BouncePlatform
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, FPS, VERTICAL_CENTER

# Initialize PyGame
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a ball instance
ball = Ball(x=SCREEN_WIDTH/2, y=100, radius=15, color=WHITE, outline_color=RED, velocity=(0, 0), gravity=-0.1, restitution=0.8)

# Clock to control game's frame rate
clock = pygame.time.Clock()

# A simple flag for controlling playback state
playback_controls = { 
    "pause": threading.Event(),  
    "stop": threading.Event(),
    "total_paused_duration": 0,
    "pause_start_time": None,
}

# Define a custom event type for MIDI note on
MIDI_NOTE_ON = pygame.USEREVENT + 1

# Initialize audio
audio.init()
audio.play_wav("music/twinkle-twinkle-little-star-non-16.wav")
global_event_queue = audio.create_global_event_queue('music/twinkle-twinkle-little-star.mid')
midi_thread = threading.Thread(target=audio.trigger_events, args=(global_event_queue, MIDI_NOTE_ON, playback_controls))
midi_thread.start()

running = True

platform = BouncePlatform(ball, length=50, width=10)

# Main game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MIDI_NOTE_ON:
            # Handle the MIDI note on event
            audio.pause_playback(playback_controls)
            ball.pause()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            audio.resume_playback(playback_controls)
            ball.resume()
            ball.bounce_off_platform(platform)
        elif event.type == pygame.MOUSEMOTION:
            # Check if the game is paused and thus in platform angle selection mode
            if playback_controls["pause"].is_set():
                # Calculate the new angle for the platform based on mouse position
                mouse_x, mouse_y = event.pos
                # Calculate the angle in radians between the mouse and the ball's center
                angle_rad = math.atan2(ball.y - mouse_y, mouse_x - ball.x)
                # Convert the angle to degrees and update the platform's angle
                platform.angle = math.degrees(angle_rad) % 360
        
        pygame.time.delay(10)  # Small delay to limit CPU usage

    vertical_offset = ball.y - VERTICAL_CENTER
    
    ball.update()
    screen.fill(BLACK)
    ball.draw(screen, y_offset=vertical_offset)
    
    if playback_controls["pause"].is_set():
        platform.draw(screen, y_offset=vertical_offset)
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

# Quit PyGame MIDI
pygame.midi.quit()
midi_thread.join()

# Quit PyGame
pygame.quit()
sys.exit()
