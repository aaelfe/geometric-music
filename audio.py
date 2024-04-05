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

# No longer in use but don't want to get rid of just yet
# def play_midi(file_path, controls, custom_event):
#     mid = mido.MidiFile(file_path)
    
#     for msg in mid.play():
#         if controls["stop"].is_set():
#             break
#         while controls["pause"].is_set() and not controls["stop"].is_set():
#             time.sleep(0.1)
#         if not msg.is_meta and msg.type == 'note_on':
#             event = pygame.event.Event(custom_event, note=msg.note, velocity=msg.velocity)
#             pygame.event.post(event)

def pause_playback(controls):
    controls["pause"].set()
    pygame.mixer.music.pause()
    controls["pause_start_time"] = time.time()

def resume_playback(controls):
    controls["pause"].clear()
    pygame.mixer.music.unpause()
    pause_duration = time.time() - controls["pause_start_time"]
    controls["total_paused_duration"] += pause_duration

def stop_playback(controls):
    controls["stop"].set()

def create_global_event_queue(midi_file_path):
    # Load the MIDI file
    midi_file = mido.MidiFile(midi_file_path)

    # Default tempo: 500,000 microseconds per beat (120 bpm)
    default_tempo = 500000
    ticks_per_beat = midi_file.ticks_per_beat
    current_tempo = default_tempo  # Start with the default tempo
    
    # This variable will hold the global event queue.
    global_event_queue = []
    
    # Calculate absolute times for events in seconds and sort them
    absolute_time_in_seconds = 0.0
    
    for track in midi_file.tracks:
        elapsed_ticks = 0
        for msg in track:
            # Update elapsed time with current message's delta time
            elapsed_ticks += msg.time
            
            # If the message is a tempo change, update the current tempo
            if msg.type == 'set_tempo':
                current_tempo = msg.tempo
            
            # Convert ticks to seconds (for the current segment)
            elapsed_seconds = mido.tick2second(elapsed_ticks, ticks_per_beat, current_tempo)
            
            if not msg.is_meta and msg.type == 'note_on' and msg.velocity > 0:
                # Store the event with the absolute time in seconds
                global_event_queue.append((absolute_time_in_seconds + elapsed_seconds, msg))
    
    # Sort the global event queue by time in seconds
    global_event_queue.sort(key=lambda x: x[0])
    
    # Now, group events that occur at the same time
    processed_queue = []
    current_time = None
    current_events = []
    tolerance = 0.01  # Tolerance for grouping events that occur at the same time
    for time, msg in global_event_queue:
        if current_time is None or abs(time - current_time) > tolerance:
            if current_events:
                processed_queue.append((current_time, current_events))
            current_time = time
            current_events = [msg]
        else:
            current_events.append(msg)
    
    # Don't forget the last set of events
    if current_events:
        processed_queue.append((current_time, current_events))
    
    return processed_queue

def trigger_builder_events(event_queue, custom_event, controls):
    start_time = time.time()  # Get the current time to use as the start time

    while event_queue:
         # Check if the playback is paused
        while controls["pause"].is_set():
            time.sleep(0.01)  # Sleep for a short duration to reduce CPU usage during pause

        # Calculate elapsed time, account for pause duration
        current_time = time.time() - start_time - controls["total_paused_duration"]  

        # Check if the first event in the queue is due to be triggered
        if event_queue[0][0] <= current_time:
            _, events_to_trigger = event_queue.pop(0)  # Remove the event from the queue

            controls["time_until_next"] = 0
            if event_queue:
                controls["time_until_next"] = event_queue[0][0] - current_time
                
            for event in events_to_trigger:
                # Your logic to handle the event goes here.
                # This could be playing a note, stopping a note, etc.
                print(f"Triggering event at {current_time}: {event}")
            event = pygame.event.Event(custom_event, note=events_to_trigger[0].note, velocity=events_to_trigger[0].velocity)
            pygame.event.post(event)
        else:
            # Sleep for a short duration to avoid busy waiting
            time.sleep(0.01)  # Adjust sleep time as needed for your application

    # now cleanup and switch state
    stop_playback(controls)

def trigger_playback_events(event_queue, custom_event, controls):
    start_time = time.time()  # Get the current time to use as the start time

    while event_queue:
        # Calculate elapsed time
        current_time = time.time() - start_time

        # Check if the first event in the queue is due to be triggered
        if event_queue[0][0] <= current_time:
            _, events_to_trigger = event_queue.pop(0)  # Remove the event from the queue
                
            for event in events_to_trigger:
                # Your logic to handle the event goes here.
                # This could be playing a note, stopping a note, etc.
                print(f"Triggering event at {current_time}: {event}")
            event = pygame.event.Event(custom_event, note=events_to_trigger[0].note, velocity=events_to_trigger[0].velocity)
            pygame.event.post(event)
        else:
            # Sleep for a short duration to avoid busy waiting
            time.sleep(0.01)  # Adjust sleep time as needed for your application

    # now cleanup and switch state
    stop_playback(controls)