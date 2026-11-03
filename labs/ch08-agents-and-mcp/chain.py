# Generated from src/content/chapters (chapter 8) by `npm run labs`. Edit the chapter, not this file.
import anthropic

from llm_utils import check_stop, response_text  # from chapter 3

client = anthropic.Anthropic()

def ask(prompt: str) -> str:
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response_text(check_stop(response))

topic = "Why our team moved from REST polling to webhooks"

# Step 1: plan
outline = ask(f"Write a 5-point outline for a blog post about: {topic}. "
              "One point per line, no other text.")

# Gate: ordinary code checks the intermediate result
points = [line for line in outline.splitlines() if line.strip()]
if len(points) != 5:
    raise ValueError(f"Expected 5 outline points, got {len(points)}")

# Step 2: write, using the checked outline
draft = ask(f"Write the blog post. Follow this outline exactly:\n\n{outline}")
print(draft)
