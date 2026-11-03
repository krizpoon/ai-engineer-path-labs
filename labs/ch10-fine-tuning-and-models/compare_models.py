# Generated from src/content/chapters (chapter 10) by `npm run labs`. Edit the chapter, not this file.
import time
import anthropic
from llm_utils import check_stop, response_text, UnusableResponse

client = anthropic.Anthropic()

# (input, output) dollars per million tokens, checked October 2026.
# Haiku's price is for prompts up to 100K tokens.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}

prompt = ("Classify this support ticket as billing, bug or feature "
          "request: 'I was charged twice for my March invoice.' "
          "Reply with one word.")

for model, (in_price, out_price) in PRICES.items():
    start = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    seconds = time.perf_counter() - start  # time to the complete answer

    usage = response.usage  # you pay for the call even if it fails
    cost = (usage.input_tokens * in_price
            + usage.output_tokens * out_price) / 1_000_000
    try:
        answer = response_text(check_stop(response)).strip()
    except UnusableResponse as err:
        answer = f"<unusable: {err}>"
    print(f"{model:20} {seconds:5.1f}s  {cost:.6f} USD  {answer}")
