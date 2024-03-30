import pygame
import pygame.midi
import mido
import threading
import sys
import ball

# Initialize PyGame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 450, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Create a ball instance
ball = ball.Ball(x=SCREEN_WIDTH/2, y=100, radius=15, color=WHITE, outline_color=RED, velocity=(0, 0))

# Clock to control game's frame rate
clock = pygame.time.Clock()
FPS = 60

# Initialize PyGame mixer
pygame.mixer.init()

# Initialize PyGame MIDI
pygame.midi.init()

# Define a custom event type for MIDI note on
MIDI_NOTE_ON = pygame.USEREVENT + 1

# Load the WAV file
sound = pygame.mixer.Sound("music/twinkle-twinkle-little-star-non-16.wav")

# Game loop flag
running = True

def play_midi_file(file_path):
    mid = mido.MidiFile(file_path)
    
    for msg in mid.play():
        if not msg.is_meta:
            # For Note On messages
            if msg.type == 'note_on':
                # Create a custom Pygame event for the MIDI note on
                event = pygame.event.Event(MIDI_NOTE_ON, note=msg.note, velocity=msg.velocity)
                pygame.event.post(event)

# Create a thread to play MIDI file
midi_thread = threading.Thread(target=play_midi_file, args=("music/twinkle-twinkle-little-star.mid",))

# Play .wav
sound.play()

# Start thread to play MIDI
midi_thread.start()

# Main game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MIDI_NOTE_ON:
            # Handle the MIDI note on event
            print(f"MIDI Note On: Note {event.note}, Velocity {event.velocity}")
        
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
