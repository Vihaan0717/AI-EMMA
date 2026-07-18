import os
import logging
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv

# Calculate absolute project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env and .llm.env
load_dotenv(os.path.join(project_root, ".env"))
load_dotenv(os.path.join(project_root, ".llm.env"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridModelRouter:
    def __init__(self):
        # 1. Initialize Local Model (Ollama)
        # Using a small, fast model ideal for AMD GPUs
        self.local_model_name = "llama3.2:1b"
        try:
            self.local_llm = OllamaLLM(model=self.local_model_name)
            logger.info(f"Local LLM ({self.local_model_name}) initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Local LLM: {e}")
            self.local_llm = None

        # 2. Initialize Cloud Model (Hugging Face)
        self.hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        # We can use a powerful model like Mistral or Llama-3 from HF API
        self.cloud_repo_id = "mistralai/Mistral-7B-Instruct-v0.2" 
        
        if self.hf_token:
            try:
                self.cloud_llm = HuggingFaceEndpoint(
                    repo_id=self.cloud_repo_id,
                    huggingfacehub_api_token=self.hf_token,
                    task="text-generation",
                    max_new_tokens=512,
                )
                logger.info(f"Cloud LLM ({self.cloud_repo_id}) initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Cloud LLM: {e}")
                self.cloud_llm = None
        else:
            logger.warning("HUGGINGFACE_API_TOKEN not found in environment. Cloud model disabled.")
            self.cloud_llm = None

    def route_prompt(self, task_type: str, prompt: str) -> str:
        """
        Routes the prompt to either the local model or the cloud model 
        based on the task complexity.
        """
        logger.info(f"Routing task: {task_type}")
        
        # Simple tasks go to Local LLM for speed & privacy
        simple_tasks = ["chat", "summarize", "extract", "smart_home"]
        
        if task_type in simple_tasks and self.local_llm:
            logger.info("-> Routing to LOCAL Model")
            return self.local_llm.invoke(prompt)
            
        # Complex tasks go to Cloud LLM for accuracy & reasoning
        elif self.cloud_llm:
            logger.info("-> Routing to CLOUD Model (Hugging Face)")
            return self.cloud_llm.invoke(prompt)
            
        # Fallback to local if cloud fails/is missing token, but task is complex
        elif self.local_llm:
            logger.warning("-> Cloud model unavailable. Falling back to LOCAL Model.")
            return self.local_llm.invoke(prompt)
            
        else:
            return "Error: No AI models are currently available."

# Example Usage (For testing purposes)
if __name__ == "__main__":
    router = HybridModelRouter()
    
    print("\n--- Testing Local Route ---")
    local_response = router.route_prompt("chat", "Say hello in one short sentence!")
    print(f"Response: {local_response}")
    
    print("\n--- Testing Cloud Route ---")
    cloud_response = router.route_prompt("complex_coding", "Write a python function to calculate fibonacci recursively.")
    print(f"Response: {cloud_response}")
