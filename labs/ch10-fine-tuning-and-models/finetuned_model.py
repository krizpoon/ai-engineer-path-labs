# Generated from src/content/chapters (chapter 10) by `npm run labs`. Edit the chapter, not this file.
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER = "ticket-classifier-lora"  # output_dir from training
SYSTEM = "Label the ticket: billing, bug or feature. " \
         "Reply with the label only."  # same as in train.jsonl

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(BASE)
base = AutoModelForCausalLM.from_pretrained(BASE)
model = PeftModel.from_pretrained(base, ADAPTER).to(device)
model.eval()  # inference only: no dropout

def finetuned_model(ticket: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": ticket},
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        output = model.generate(
            **inputs, max_new_tokens=5, do_sample=False)
    prompt_length = inputs["input_ids"].shape[1]
    reply = tokenizer.decode(
        output[0][prompt_length:], skip_special_tokens=True)
    return reply.strip().lower()

if __name__ == "__main__":
    print(finetuned_model("I was charged twice in March."))  # billing
