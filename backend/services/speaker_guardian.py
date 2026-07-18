import os
import torch
import numpy as np
import logging
from typing import Optional
from speechbrain.inference.speaker import SpeakerRecognition

logger = logging.getLogger("SpeakerGuardian")

class SpeakerGuardian:
    """
    NEXUS-X Voice Biometric Security.
    Verifies the identity of the speaker using SpeechBrain (ECAPA-TDNN).
    """
    def __init__(self, reference_path: str = "Kanna_Voice_Print.wav"):
        self.reference_path = reference_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._has_reference = os.path.exists(self.reference_path)
        self.verification = None
        
        logger.info(f"Initializing SpeakerGuardian on {self.device}...")
        try:
            self.verification = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                run_opts={"device": self.device}
            )
            if not self._has_reference:
                logger.warning(f"Reference voice print not found at {self.reference_path}. Security will be in BYPASS mode.")
        except Exception as e:
            logger.error(f"Failed to initialize SpeakerRecognition: {e}")

    def is_authorized(self, audio_data: np.ndarray, threshold: float = 0.25) -> bool:
        """
        Verifies if the provided audio matches the reference voice print.
        Returns True if authorized or if in bypass mode (no reference file).
        """
        if not self._has_reference or self.verification is None:
            return True  # Bypass mode
            
        try:
            # SpeechBrain expects a torch tensor
            audio_tensor = torch.from_numpy(audio_data).float().to(self.device)
            # Add batch dimension
            audio_tensor = audio_tensor.unsqueeze(0)
            
            # Load and process reference
            # Note: In a production loop, we'd pre-calculate the reference embedding
            # but for this initial version, we'll use verify_files or simple embedding comparison.
            
            # For real-time processing, we use the internal embedding comparison
            # We'll save the live chunk to a temp file for the SpeechBrain helper or process directly
            import tempfile
            import soundfile as sf
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
                sf.write(tmp_path, audio_data, 16000)
            
            score, prediction = self.verification.verify_files(self.reference_path, tmp_path)
            os.unlink(tmp_path)
            
            # prediction is a boolean tensor [True/False]
            is_match = bool(prediction[0])
            logger.debug(f"Speaker verification score: {score[0]:.4f} | Match: {is_match}")
            return is_match
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return True # Fail-safe to allowed in case of system error

if __name__ == "__main__":
    # Standalone test
    logging.basicConfig(level=logging.INFO)
    guardian = SpeakerGuardian()
    print("Speaker Guardian Ready.")
    if not guardian._has_reference:
        print("!!! Please record 30s of your voice and save it as 'Kanna_Voice_Print.wav' to test security.")
