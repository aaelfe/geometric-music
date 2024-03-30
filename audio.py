import pygame
import pygame.midi
import mido
import time

def init():
    pygame.mixer.init()
    pygame.midi.init()

def play_wav(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play(-1)

def play_midi(file_path, controls, custom_event):
    mid = mido.MidiFile(file_path)
    
    for msg in mid.play():
        if controls["stop"].is_set():
            break
        while controls["pause"].is_set() and not controls["stop"].is_set():
            time.sleep(0.1)
        if not msg.is_meta and msg.type == 'note_on':
            event = pygame.event.Event(custom_event, note=msg.note, velocity=msg.velocity)
            pygame.event.post(event)

def pause_playback(controls):
    controls["pause"].set()
    pygame.mixer.music.pause()

def resume_playback(controls):
    controls["pause"].clear()
    pygame.mixer.music.unpause()

def stop_playback(controls):
    controls["stop"].set()
