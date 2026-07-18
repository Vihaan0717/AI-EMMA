import os
import logging
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_path = os.path.join(project_root, "data", "training", "synthetic_data.jsonl")
output_dir = os.path.join(project_root, "models", "jarvis_custom")

def main():
    if not os.path.exists(data_path):
        logger.error(f"Training data not found at {data_path}. Please run Phase 3 (!synthesize) first.")
        return

    # 1. Load the Dataset
    logger.info("Loading synthetic training data...")
    dataset = load_dataset("json", data_files=data_path, split="train")

    def format_instruction(example):
        """Formats the jsonl data into a chat prompt the model understands."""
        return f"User: {example['instruction']}\nAssistant: {example['output']}"

    # 2. Setup Base Model and Tokenizer
    # We use a very small base model so it fits in AMD VRAM
    model_id = "meta-llama/Llama-3.2-1B"
    logger.info(f"Loading base model: {model_id}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token

    # Load model in 16-bit precision to save VRAM
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto" # Automatically maps to GPU if available
    )

    # 3. Apply LoRA (Low-Rank Adaptation)
    # This prevents the computer from crashing by only training 1% of the model's brain
    logger.info("Applying LoRA configuration...")
    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 4. Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=1,  # Keep this low for limited VRAM
        gradient_accumulation_steps=4,  # Simulates a larger batch size
        num_train_epochs=3,             # Number of times to loop through the data
        learning_rate=2e-4,
        logging_steps=10,
        save_strategy="epoch",
        optim="adamw_torch",
        fp16=True,                      # Use Mixed Precision
    )

    # 5. Initialize Trainer
    logger.info("Initializing SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=1024,
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=format_instruction, # Applies our format
    )

    # 6. Start Training
    logger.info("🔥 Starting training process...")
    trainer.train()

    # 7. Save the Custom Model
    logger.info(f"Training complete! Saving custom model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

if __name__ == "__main__":
    main()
