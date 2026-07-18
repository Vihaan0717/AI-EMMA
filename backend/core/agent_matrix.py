import os
import logging
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv

# Calculate absolute project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(os.path.join(project_root, ".env"))
load_dotenv(os.path.join(project_root, ".llm.env"))

logger = logging.getLogger(__name__)

class AgentMatrix:
    def __init__(self):
        # 1. Initialize The Critic (Local Fast Model)
        self.critic_model_name = "llama3.2:1b"
        try:
            self.critic = OllamaLLM(model=self.critic_model_name)
            logger.info(f"Matrix Critic ({self.critic_model_name}) initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Critic: {e}")
            self.critic = None

        # 2. Initialize The Solver (Cloud Expert Model)
        self.hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.solver_repo_id = "mistralai/Mistral-7B-Instruct-v0.2" 
        
        if self.hf_token:
            try:
                self.solver = HuggingFaceEndpoint(
                    repo_id=self.solver_repo_id,
                    huggingfacehub_api_token=self.hf_token,
                    task="text-generation",
                    max_new_tokens=1024,
                )
                logger.info(f"Matrix Solver ({self.solver_repo_id}) initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Solver: {e}")
                self.solver = None
        else:
            logger.error("HUGGINGFACE_API_TOKEN missing. Matrix Solver offline.")
            self.solver = None

    def simulate(self, problem: str, max_rounds: int = 3, progress_callback=None) -> str:
        """
        Runs the simulation loop where the Solver generates an answer and the Critic reviews it.
        progress_callback is a function that can stream updates back to the user (e.g. Telegram).
        """
        if not self.solver or not self.critic:
            return "Matrix offline: Both Solver and Critic must be initialized."

        current_answer = ""
        
        def notify(msg):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        for round_num in range(1, max_rounds + 1):
            notify(f"🔄 **Matrix Round {round_num}/{max_rounds}**")
            
            # 1. The Solver attempts the problem
            notify("🧠 *The Solver is thinking...*")
            if round_num == 1:
                solver_prompt = f"Solve the following problem comprehensively:\n{problem}"
            else:
                solver_prompt = f"You are solving: {problem}\n\nYour previous answer had flaws based on the Critic's feedback:\n{critic_feedback}\n\nPlease provide a completely revised and perfected answer."
            
            try:
                current_answer = self.solver.invoke(solver_prompt)
            except Exception as e:
                notify(f"⚠️ Solver Error: {e}")
                return current_answer

            # 2. The Critic reviews the answer
            notify("⚖️ *The Critic is analyzing the answer for hallucinations or logic errors...*")
            critic_prompt = f"""
            You are an aggressive, perfectionist Critic Agent.
            The Original Problem is: {problem}
            The Solver's Answer is: {current_answer}
            
            Analyze the answer. If you find any logic errors, hallucinations, or missing details, clearly list them. 
            If the answer is absolutely perfect and flawless, output exactly the word: APPROVED.
            """
            
            try:
                critic_feedback = self.critic.invoke(critic_prompt).strip()
            except Exception as e:
                notify(f"⚠️ Critic Error: {e}")
                return current_answer
                
            if "APPROVED" in critic_feedback.upper():
                notify("✅ **The Critic APPROVED the answer!**")
                break
            else:
                notify(f"❌ **The Critic REJECTED the answer!**\nFeedback: {critic_feedback[:100]}...")
                if round_num == max_rounds:
                    notify("⚠️ Max rounds reached. Delivering best attempt.")
        
        return current_answer

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    matrix = AgentMatrix()
    print("\n--- Testing Agent Matrix ---")
    final_result = matrix.simulate("If a plane crashes exactly on the border of the US and Canada, where do they bury the survivors?")
    print(f"\nFinal Result:\n{final_result}")
