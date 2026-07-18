import os
import logging
from TTS.api import TTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceCloner:
    """Uses Coqui TTS (XTTS-v2) for zero-shot voice cloning."""

    def __init__(self, output_dir: str = "./synthesized_audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("Loading Coqui TTS (XTTS-v2) model. This requires accepting their terms of service.")
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            # XTTS-v2 allows voice cloning from a short reference audio clip
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            logger.info(f"TTS Model loaded on {device}.")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            self.tts = None

    def clone_and_speak(self, text: str, reference_audio_path: str, output_filename: str) -> str:
        """
        Synthesizes 'text' using the voice found in 'reference_audio_path'.
        Saves the output to the output_dir.
        """
        if not self.tts:
            raise RuntimeError("TTS model is not loaded.")
        
        output_path = os.path.join(self.output_dir, output_filename)
        logger.info(f"Synthesizing speech. Ref: {reference_audio_path} -> Output: {output_path}")
        
        try:
            self.tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio_path,
                language="en",
                file_path=output_path
            )
            logger.info("Speech synthesis complete.")
            return output_path
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return ""

if __name__ == "__main__":
    print("VoiceCloner initialized. Note: Requires Coqui TTS model download on first run.")
