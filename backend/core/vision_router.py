import os
import base64
import logging
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

class VisionRouter:
    def __init__(self):
        self.model_name = "llava"
        try:
            # We use OllamaLLM for the vision model as well.
            # LLaVA naturally accepts images in base64 format via Ollama.
            self.vision_llm = OllamaLLM(model=self.model_name)
            logger.info(f"Vision Router initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Vision Router: {e}")
            self.vision_llm = None

    def encode_image(self, image_path: str) -> str:
        """Encodes an image file to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail. Identify any objects, read any visible text, and explain the context.") -> str:
        """
        Sends the image to the local LLaVA model for analysis.
        """
        if not self.vision_llm:
            return "Vision system is currently offline or uninitialized."
            
        if not os.path.exists(image_path):
            return f"Error: Image not found at {image_path}"

        logger.info(f"Analyzing image: {image_path}")
        
        try:
            # Encode the image
            base64_image = self.encode_image(image_path)
            
            # Using the invoke method with raw bindings to pass the image to Ollama
            # Ollama expects 'images' as a list of base64 strings in the kwargs
            response = self.vision_llm.invoke(
                prompt,
                images=[base64_image]
            )
            
            logger.info("Image analysis complete.")
            return response
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return f"Failed to analyze image: {e}"

# Simple test block
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    router = VisionRouter()
    print("Vision Router Ready.")
