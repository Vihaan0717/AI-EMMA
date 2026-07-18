import logging
import os
import subprocess
import tempfile
import ollama # Make sure to run `pip install ollama yt-dlp`

logger = logging.getLogger("jarvis.reel_analyzer")

class ReelAnalyzer:
    """
    Downloads and analyzes Instagram Reels using a local LLM via Ollama.
    """
    def __init__(self, model_name: str = "llama3.1"):
        self.model_name = model_name
        
    def download_reel(self, url: str) -> str:
        """Downloads the video using yt-dlp and returns the path."""
        logger.info(f"[ReelAnalyzer] Downloading reel from {url}...")
        output_path = os.path.join(tempfile.gettempdir(), "reel_%(id)s.%(ext)s")
        try:
            # yt-dlp can download from Instagram public links easily
            cmd = ["yt-dlp", "-o", output_path, url]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Find the downloaded file
            for f in os.listdir(tempfile.gettempdir()):
                if f.startswith("reel_"):
                    return os.path.join(tempfile.gettempdir(), f)
            return ""
        except Exception as e:
            logger.error(f"[ReelAnalyzer] Failed to download reel: {e}")
            return ""

    def analyze_video(self, video_path: str) -> str:
        """
        Since Llama3.1 natively isn't multimodal, we would ideally use llava.
        For this placeholder, we mock the vision extraction, but if the user has llava,
        we can pass base64 encoded frames to the ollama client.
        """
        logger.info(f"[ReelAnalyzer] Analyzing video file: {video_path} using {self.model_name}...")
        
        # Real implementation would use ffmpeg to extract frames/audio,
        # transcribe audio with whisper, and describe frames with llava.
        # Then pass the combined transcript + descriptions to Llama3.
        
        prompt = (
            "You are JARVIS. I am providing you with the transcript and visual description of an Instagram Reel. "
            "Please summarize what the reel is about, the humor or context, and what it implies about the user's preference."
        )
        
        # Placeholder call to Ollama
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'system',
                    'content': prompt
                },
                {
                    'role': 'user',
                    'content': "Transcript: 'Look at this cute cat playing piano!' Visual: A tabby cat hitting keys on a synthesizer."
                }
            ])
            return response['message']['content']
        except Exception as e:
            logger.error(f"[ReelAnalyzer] Ollama generation failed: {e}")
            return "Failed to analyze the reel."

if __name__ == "__main__":
    analyzer = ReelAnalyzer()
    print(analyzer.analyze_video("mock_path.mp4"))
