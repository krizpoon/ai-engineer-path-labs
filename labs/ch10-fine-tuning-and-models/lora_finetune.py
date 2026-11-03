# Generated from src/content/chapters (chapter 10) by `npm run labs`. Edit the chapter, not this file.
from datasets import load_dataset
from peft import LoraConfig
from trl import SFTConfig, SFTTrainer

# Chat-formatted examples like the train.jsonl shown earlier.
dataset = load_dataset("json", data_files="train.jsonl", split="train")

lora = LoraConfig(
    r=8,                # rank: size of the A and B matrices
    lora_alpha=16,      # scaling for the correction
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],  # which weight matrices get adapters
    task_type="CAUSAL_LM",
)

trainer = SFTTrainer(
    model="Qwen/Qwen2.5-0.5B-Instruct",  # small open-weight base model
    train_dataset=dataset,
    peft_config=lora,
    args=SFTConfig(
        output_dir="ticket-classifier-lora",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
    ),
)

trainer.train()
trainer.save_model()  # writes the small adapter, not a full model copy
