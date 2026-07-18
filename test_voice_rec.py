import sounddevice as sd
import numpy as np
import queue
import sys
import logging
from voice.whisper_listener import WhisperListener

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("voice_test")

def test_voice_rec():
    print("\n" + "="*50)
    print("JARVIS VOICE RECOGNITION TEST")
    print("Speak now... (Press Ctrl+C to stop)")
    print("="*50 + "\n")

    # Initialize Whisper Listener
    # Using 'base' for better accuracy than 'tiny', while still remaining fast on CPU.
    try:
        listener = WhisperListener(model_size="base", device="cpu", compute_type="int8")
    except Exception as e:
        logger.error(f"Failed to initialize Whisper: {e}")
        return

    def on_transcript(text, lang):
        print(f"\n>>> Detected ({lang}): {text}")

    listener.set_callback(on_transcript)
    listener.start()

    # Audio recording settings
    fs = 16000  # Whisper expects 16kHz
    channels = 1
    block_duration = 1.0  # 1 second blocks
    blocksize = int(fs * block_duration)
    
    try:
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio status: {status}")
            
            # Convert float32 [-1, 1] to int16
            audio_int16 = (indata * 32768).astype(np.int16)
            listener.add_audio_chunk(audio_int16.tobytes())

        with sd.InputStream(samplerate=fs, channels=channels, blocksize=blocksize, callback=audio_callback):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopping test...")
    except Exception as e:
        logger.error(f"Error during recording: {e}")
    finally:
        listener.stop()
        print("Test finished.")

if __name__ == "__main__":
    test_voice_rec()
