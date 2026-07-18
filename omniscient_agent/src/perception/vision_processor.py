import cv2
import os
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionProcessor:
    """Handles extraction and pre-processing of video frames for LLM analysis."""

    def __init__(self, output_dir: str = "./frames"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_frames(self, video_path: str, frame_interval_seconds: int = 5) -> List[str]:
        """
        Extracts frames from a video at a specified interval.
        Returns a list of file paths to the saved frames.
        """
        logger.info(f"Extracting frames from {video_path} every {frame_interval_seconds} seconds.")
        extracted_frames = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return extracted_frames

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval_frames = int(fps * frame_interval_seconds)
        
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval_frames == 0:
                timestamp = int(frame_count / fps)
                # Ensure filename is unique by timestamp
                frame_filename = os.path.join(self.output_dir, f"frame_{timestamp:05d}s.jpg")
                cv2.imwrite(frame_filename, frame)
                extracted_frames.append(frame_filename)
                saved_count += 1
                
            frame_count += 1

        cap.release()
        logger.info(f"Finished extracting {saved_count} frames.")
        return extracted_frames

if __name__ == "__main__":
    print("VisionProcessor initialized. Call extract_frames(video_path) to use.")
