import os
import json
import logging
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(project_root, ".env"))
load_dotenv(os.path.join(project_root, ".llm.env"))

logger = logging.getLogger(__name__)

class DataSynthesizer:
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        # We use a smart model to generate high-quality data
        self.teacher_repo_id = "mistralai/Mistral-7B-Instruct-v0.2" 
        
        self.output_dir = os.path.join(project_root, "data", "training")
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_file = os.path.join(self.output_dir, "synthetic_data.jsonl")

        if self.hf_token:
            try:
                self.teacher = HuggingFaceEndpoint(
                    repo_id=self.teacher_repo_id,
                    huggingfacehub_api_token=self.hf_token,
                    task="text-generation",
                    max_new_tokens=1500,
                    temperature=0.7
                )
                logger.info(f"Teacher Model ({self.teacher_repo_id}) initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Teacher: {e}")
                self.teacher = None
        else:
            logger.error("HUGGINGFACE_API_TOKEN missing. Teacher offline.")
            self.teacher = None

    def generate_data(self, topic: str, count: int = 3, progress_callback=None) -> str:
        """
        Asks the Teacher model to generate `count` Q&A pairs about `topic`
        and saves them to a jsonl file for future fine-tuning.
        """
        if not self.teacher:
            return "Teacher model offline. Cannot generate synthetic data."

        def notify(msg):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        notify(f"🎓 **Teacher Model generating {count} training examples on:** `{topic}`")

        prompt = f"""
        Generate {count} distinct, high-quality, complex Question and Answer pairs about the topic: {topic}.
        
        Format the output EXACTLY as a JSON array of objects. 
        Each object must have exactly two keys: "instruction" and "output".
        Do not include any markdown formatting, backticks, or other text outside the JSON array.
        
        Example format:
        [
            {{"instruction": "Question 1 goes here", "output": "Detailed answer 1 goes here"}},
            {{"instruction": "Question 2 goes here", "output": "Detailed answer 2 goes here"}}
        ]
        """

        try:
            response = self.teacher.invoke(prompt).strip()
            
            # Clean up the response in case the model added markdown blocks
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            try:
                data_pairs = json.loads(response)
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse JSON from Teacher: {response}")
                return "⚠️ Teacher generated invalid format. Could not save data."

            saved_count = 0
            with open(self.output_file, 'a', encoding='utf-8') as f:
                for pair in data_pairs:
                    if "instruction" in pair and "output" in pair:
                        # Convert to standard Alpaca JSONL format
                        jsonl_entry = {
                            "instruction": pair["instruction"],
                            "input": "",
                            "output": pair["output"]
                        }
                        f.write(json.dumps(jsonl_entry) + '\n')
                        saved_count += 1

            notify(f"✅ Successfully saved {saved_count} new examples to the vault!")
            return f"Generated {saved_count} examples successfully."

        except Exception as e:
            logger.error(f"Data synthesis failed: {e}")
            return f"⚠️ Generation failed: {e}"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    synth = DataSynthesizer()
    print("--- Testing Data Synthesizer ---")
    synth.generate_data("Basic Python List Comprehensions", count=1)
