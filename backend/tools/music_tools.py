import os
import struct
import logging

logger = logging.getLogger("MusicTools")

NOTE_SEMITONES = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

def note_name_to_midi(note_name: str) -> int:
    """Converts a note name (e.g., 'C4', 'F#5') to MIDI number."""
    note_name = note_name.strip()
    if not note_name:
        return 60  # Default to middle C
        
    pattern = re.match(r"^([A-Ga-g]#?|b?)(-?\d+)$", note_name)
    if not pattern:
        # Try finding semitones with regex
        m = re.match(r"^([A-G][#b]?)(-?\d+)$", note_name, re.IGNORECASE)
        if not m:
            return 60
        name, octave = m.groups()
    else:
        name, octave = pattern.groups()
        
    # Standardize name
    name = name[0].upper() + name[1:]
    semitone = NOTE_SEMITONES.get(name, 0)
    octave_num = int(octave)
    
    return 12 * (octave_num + 1) + semitone

import re

def write_vlq(value: int) -> bytes:
    """Helper to write variable-length quantity (VLQ) for MIDI delay times."""
    buffer = bytearray()
    buffer.append(value & 0x7F)
    value >>= 7
    while value > 0:
        buffer.insert(0, (value & 0x7F) | 0x80)
        value >>= 7
    return bytes(buffer)

def create_midi_file(notes: list, output_path: str, tempo: int = 120, ticks_per_beat: int = 480) -> bool:
    """
    Generates a single-track MIDI file (Format 0) from a list of note events.
    
    Each note event in `notes` should be a dict:
        {
            'note': 'C4' (str or int midi pitch),
            'start': float (beats from start),
            'duration': float (beats),
            'velocity': int (0-127, optional, default 64)
        }
    """
    try:
        # Convert all notes to absolute tick times
        events = []
        for n in notes:
            pitch = n['note']
            if isinstance(pitch, str):
                pitch = note_name_to_midi(pitch)
            
            start_tick = int(n['start'] * ticks_per_beat)
            duration_ticks = int(n['duration'] * ticks_per_beat)
            end_tick = start_tick + duration_ticks
            velocity = n.get('velocity', 64)
            
            # Event format: (tick_time, type, pitch, velocity)
            events.append((start_tick, 'on', pitch, velocity))
            events.append((end_tick, 'off', pitch, 0))
            
        # Sort events by tick time. If ticks are equal, 'off' comes before 'on'
        events.sort(key=lambda x: (x[0], 0 if x[1] == 'off' else 1))
        
        # Build track events list with delta times
        track_data = bytearray()
        
        # Add Tempo Meta Event: FF 51 03 (3 bytes microsecs per beat)
        # Microseconds per beat = 60,000,000 / BPM
        us_per_beat = int(60000000 / tempo)
        tempo_bytes = struct.pack(">I", us_per_beat)[1:]  # 3 bytes
        
        # Delta time 0 for tempo setup
        track_data.extend(write_vlq(0))
        track_data.extend(b'\xFF\x51\x03' + tempo_bytes)
        
        current_tick = 0
        for tick, ev_type, pitch, velocity in events:
            delta = tick - current_tick
            current_tick = tick
            
            # Write delta time
            track_data.extend(write_vlq(delta))
            
            # Write MIDI Note On/Off
            status = 0x90 if ev_type == 'on' else 0x80
            track_data.append(status)
            track_data.append(pitch)
            track_data.append(velocity)
            
        # End of Track Event: FF 2F 00
        track_data.extend(write_vlq(0))
        track_data.extend(b'\xFF\x2F\x00')
        
        # Write headers
        # MThd header chunk: chunk type (4 bytes), length (4 bytes), format (2 bytes), tracks (2 bytes), division (2 bytes)
        mthd = b'MThd' + struct.pack(">IHHH", 6, 0, 1, ticks_per_beat)
        
        # MTrk chunk: chunk type (4 bytes), chunk length (4 bytes), data
        mtrk = b'MTrk' + struct.pack(">I", len(track_data)) + track_data
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(mthd + mtrk)
            
        logger.info(f"MIDI successfully created: {output_path} ({len(notes)} notes)")
        return True
    except Exception as e:
        logger.error(f"Failed to create MIDI file: {e}")
        return False

def parse_abc_notation(abc_text: str) -> list:
    """
    Decodes basic ABC notation into a list of notes with start times and durations.
    Example input: "C D E F G A B c" (one beat per note)
    """
    notes = []
    current_time = 0.0
    
    # Clean and split notes (very basic parser)
    # Replaces headers and works on the actual notes block
    lines = abc_text.strip().split("\n")
    note_lines = [l for l in lines if not any(l.startswith(h + ":") for h in "X T M L K Q R Z C V P o s d w")]
    
    notes_str = " ".join(note_lines)
    # Find note symbols like C, D, E, F, G, A, B, c, d, e, f, g, a, b, and accidentals/durations
    # Simple regex to catch note letter, optional accidental, optional octave indicator, optional duration multiplier/divisor
    note_pattern = re.compile(r"([\^_=]?[A-Ga-g][,']*)(\d*/?\d*)")
    
    matches = note_pattern.findall(notes_str)
    
    for note_symbol, dur_modifier in matches:
        if not note_symbol:
            continue
            
        # Map letter to base pitch & octave
        letter = note_symbol[0]
        is_lowercase = letter.islower()
        base_letter = letter.upper()
        
        # Base octave is 4 for uppercase, 5 for lowercase
        octave = 5 if is_lowercase else 4
        
        # Adjust octave based on commas (down) or apostrophes (up)
        for char in note_symbol[1:]:
            if char == ',':
                octave -= 1
            elif char == "'":
                octave += 1
                
        # Resolve accidental (accidentals prefix note in ABC)
        accidental = ""
        # Check if the note_symbol starts with accidental marker
        if note_symbol.startswith("^"):
            accidental = "#"
        elif note_symbol.startswith("_"):
            accidental = "b"
            
        note_name = f"{base_letter}{accidental}{octave}"
        
        # Resolve duration modifier
        duration = 1.0  # default 1 beat
        if dur_modifier:
            if "/" in dur_modifier:
                parts = dur_modifier.split("/")
                numerator = float(parts[0]) if parts[0] else 1.0
                denominator = float(parts[1]) if parts[1] else 2.0
                duration = numerator / denominator
            else:
                duration = float(dur_modifier)
                
        notes.append({
            'note': note_name,
            'start': current_time,
            'duration': duration,
            'velocity': 80
        })
        current_time += duration
        
    return notes
