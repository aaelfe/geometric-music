import pygame
import pygame.midi
import threading
import sys
import audio
from ball import Ball
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, FPS

# Initialize PyGame
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a ball instance
ball = Ball(x=SCREEN_WIDTH/2, y=100, radius=15, color=WHITE, outline_color=RED, velocity=(0, 0))

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

# Main game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MIDI_NOTE_ON:
            # Handle the MIDI note on event
            audio.pause_playback(playback_controls)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            audio.resume_playback(playback_controls)
        
        pygame.time.delay(10)  # Small delay to limit CPU usage
    
    # Game logic
    ball.update()
    
    # Clear the screen
    screen.fill(BLACK)
    
    # Draw the ball
    ball.draw(screen)
    
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
