import whisper
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioTranscriber:
    """Handles audio transcription using OpenAI Whisper."""

    def __init__(self, model_size: str = "base"):
        """
        Initializes the Whisper model.
        Options for model_size: 'tiny', 'base', 'small', 'medium', 'large'
        """
        logger.info(f"Loading Whisper model '{model_size}' (this may take a moment)...")
        try:
            self.model = whisper.load_model(model_size)
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribes an audio or video file.
        Returns a dictionary containing 'text' and 'segments' with timestamps.
        """
        if not self.model:
            raise RuntimeError("Whisper model is not loaded.")
            
        logger.info(f"Starting transcription for: {audio_path}")
        try:
            result = self.model.transcribe(audio_path)
            logger.info("Transcription completed.")
            return result
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"text": "", "segments": []}

if __name__ == "__main__":
    # Test block - requires an actual audio/video file to run successfully
    print("AudioTranscriber initialized. Call transcribe(path) to test.")
