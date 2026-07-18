import os
import logging
from pyannote.audio import Pipeline
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeakerDiarization:
    """Handles identifying who is speaking and when."""

    def __init__(self):
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if not hf_token:
            logger.warning("HUGGINGFACE_TOKEN not found in .env. Diarization will fail.")
        
        logger.info("Loading PyAnnote Diarization Pipeline...")
        try:
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            # Send to GPU if available
            import torch
            if torch.cuda.is_available():
                self.pipeline.to(torch.device("cuda"))
                logger.info("Using GPU for diarization.")
            else:
                logger.info("Using CPU for diarization.")
        except Exception as e:
            logger.error(f"Failed to load PyAnnote pipeline: {e}")
            self.pipeline = None

    def diarize_audio(self, audio_path: str):
        """
        Processes an audio file and returns segments labeled by speaker.
        """
        if not self.pipeline:
            raise RuntimeError("Diarization pipeline is not loaded.")
        
        logger.info(f"Running diarization on {audio_path}...")
        try:
            diarization = self.pipeline(audio_path)
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            logger.info(f"Diarization complete. Found {len(set([s['speaker'] for s in segments]))} speakers.")
            return segments
        except Exception as e:
            logger.error(f"Diarization failed: {e}")
            return []

if __name__ == "__main__":
    print("SpeakerDiarization initialized. Requires HUGGINGFACE_TOKEN.")
