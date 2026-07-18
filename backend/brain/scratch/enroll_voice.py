import sounddevice as sd
import soundfile as sf
import time
import os
import sys
from pathlib import Path

def safe_print(text):
    print("".join(c if ord(c) < 128 else '?' for c in str(text)))

def enroll_voice():
    safe_print("===================================================")
    safe_print("   NEXUS-X VOICE BIOMETRIC ENROLLMENT")
    safe_print("===================================================")
    safe_print("\nInstructions:")
    safe_print("1. You will need to speak for 30 seconds.")
    safe_print("2. Speak naturally - talk about your day, your goals, or read a book.")
    safe_print("3. Try to maintain a consistent distance from the mic.")
    
    input("\nPress ENTER when you are ready to start recording...")
    
    fs = 16000  # Sample rate
    duration = 30  # Seconds
    
    safe_print(f"\n[RECORDING] Please speak now for {duration} seconds...")
    
    try:
        # Record audio
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        
        # Simple progress bar
        for i in range(duration):
            time.sleep(1)
            sys.stdout.write(f"\rProgress: [{'=' * (i+1)}{' ' * (duration-i-1)}] {i+1}s/{duration}s")
            sys.stdout.flush()
            
        sd.wait()  # Wait for recording to finish
        safe_print("\n\n[DONE] Recording complete.")
        
        # Save the reference print
        output_path = "Kanna_Voice_Print.wav"
        sf.write(output_path, recording, fs)
        
        safe_print(f"\n[SUCCESS] Reference voice print saved to: {os.path.abspath(output_path)}")
        safe_print("SpeakerGuardian will now use this to verify your identity.")
        
    except Exception as e:
        safe_print(f"\n[ERROR] Enrollment failed: {e}")

if __name__ == "__main__":
    enroll_voice()
