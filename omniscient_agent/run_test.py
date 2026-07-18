import os
import sys
import logging
from dotenv import load_dotenv

# Ensure the correct paths are loaded
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omniscient_agent.src.metadata.metadata_manager import MetadataManager
from omniscient_agent.src.analysis.narrative_analyst import NarrativeAnalyst
from omniscient_agent.src.perception.video_acquisition import VideoAcquisition

load_dotenv()

# Map HF_TOKEN from .env to HUGGINGFACE_TOKEN if needed
if os.getenv("HF_TOKEN") and not os.getenv("HUGGINGFACE_TOKEN"):
    os.environ["HUGGINGFACE_TOKEN"] = os.getenv("HF_TOKEN")

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_omniscient_pipeline():
    logger.info("--- Starting Omniscient Agent Test Pipeline ---")
    
    # 1. Metadata Search
    logger.info("\n[Phase 1] Testing Metadata Search (Jikan API)...")
    metadata_manager = MetadataManager()
    anime_info = metadata_manager.search_content("Naruto", content_type="anime")
    if anime_info:
        logger.info(f"SUCCESS: Found {anime_info['title']} (Score: {anime_info['score']})")
    else:
        logger.error("FAILED to find anime metadata.")

    # 2. Video Acquisition (Extracting stream, not downloading to save time/bandwidth)
    logger.info("\n[Phase 2] Testing Video Acquisition (yt-dlp)...")
    video_acq = VideoAcquisition()
    # A short public domain video URL for testing yt-dlp extraction safely
    test_url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    stream_url = video_acq.get_stream_url(test_url)
    if stream_url:
        logger.info("SUCCESS: Extracted stream URL successfully.")
    else:
        logger.error("FAILED to extract stream URL.")

    # 3. Narrative Analyst (Gemini API)
    logger.info("\n[Phase 3] Testing Deep Narrative Analyst (Gemini API)...")
    analyst = NarrativeAnalyst()
    
    mock_transcript = "Naruto: I will never give up! That's my nindo, my ninja way!"
    mock_visuals = "A battered young ninja stands up, bruised but determined, glaring fiercely at a powerful enemy."
    
    analysis = analyst.analyze_scene(mock_transcript, mock_visuals)
    if analysis and "Analysis failed" not in analysis:
        logger.info("SUCCESS: Narrative Analysis generated:")
        print("-" * 40)
        print(analysis)
        print("-" * 40)
    else:
        logger.error("FAILED to generate narrative analysis. Check GEMINI_API_KEY.")

    logger.info("\n--- Test Pipeline Completed ---")

if __name__ == "__main__":
    test_omniscient_pipeline()
