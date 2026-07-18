import subprocess
import os
import sys

def extract_slice(input_path, output_path, start_time="00:00:10", duration="10"):
    """
    Extracts a slice of audio using ffmpeg.
    Converts to 16kHz, mono, 16-bit WAV (ideal for XTTSv2).
    """
    print(f"Slicing {input_path} from {start_time} for {duration} seconds...")
    cmd = [
        "ffmpeg", "-y",
        "-ss", start_time,
        "-i", input_path,
        "-t", duration,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"Successfully created voice sample: {output_path}")
            return True
        else:
            print(f"ffmpeg failed: {res.stderr}")
            return False
    except Exception as e:
        print(f"Error executing ffmpeg: {e}")
        return False

if __name__ == "__main__":
    input_file = os.path.join("Voicesamp", "audio [vocals].mp3")
    output_file = os.path.join("Voicesamp", "female_ref.wav")
    
    # Slice 10 seconds starting at 15 seconds (typical start of clean speech)
    success = extract_slice(input_file, output_file, start_time="00:00:15", duration="10")
    if not success:
        sys.exit(1)
