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

platforms = []

# Main game loop
while running:
    screen.fill(BLACK)
    vertical_offset = ball.y - VERTICAL_CENTER

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MIDI_NOTE_ON:
            # Handle the MIDI note on event
            audio.pause_playback(playback_controls)
            ball.pause()

            new_platform = BouncePlatform(ball, length=50, width=10)
            platforms.append(new_platform)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            audio.resume_playback(playback_controls)
            ball.resume()
            ball.bounce_off_platform(platforms[-1])

        # event during pauses
        elif event.type == pygame.MOUSEMOTION and playback_controls["pause"].is_set():
            # Calculate the new angle for the platform based on mouse position
            mouse_x, mouse_y = event.pos
            # Calculate the angle in radians between the mouse and the ball's center
            angle_rad = math.atan2(ball.y - mouse_y, mouse_x - ball.x)
            # Convert the angle to degrees and update the platform's angle
            platforms[-1].angle = math.degrees(angle_rad) % 360

            # Now, project the bounce path based on the new angle
            projected_path = ball.project_bounce_path(platforms[-1].angle)
            
            # Draw the projected path (simplified example)
            for point in projected_path:
                adjusted_point = (point[0], point[1] - vertical_offset)
                pygame.draw.circle(screen, RED, adjusted_point, 3)  # Draw small red circles along the path
        
        pygame.time.delay(10)  # Small delay to limit CPU usage
    
    ball.update()
    ball.draw(screen, y_offset=vertical_offset)

    for i, platform in enumerate(platforms):
        is_recent = (i == len(platforms) - 1)
        platform.draw(screen, y_offset=vertical_offset, is_recent=is_recent)
    
    if playback_controls["pause"].is_set():
        platforms[-1].draw(screen, y_offset=vertical_offset)
    
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
