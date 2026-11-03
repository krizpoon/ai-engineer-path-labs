# Generated from src/content/chapters (chapter 10) by `npm run labs`. Edit the chapter, not this file.
import json
import anthropic
from llm_utils import check_stop, response_text, UnusableResponse

client = anthropic.Anthropic()
SYSTEM = "Label the ticket: billing, bug or feature. " \
         "Reply with the label only."
LABELS = {"billing", "bug", "feature"}

# Real tickets with personal data removed, and none from test.jsonl.
with open("tickets.txt") as f:
    tickets = [line.strip() for line in f if line.strip()]

kept = skipped = 0
with open("train.jsonl", "w") as out:
    for ticket in tickets:
        response = client.messages.create(
            model="claude-opus-5-5",
            max_tokens=1000,
            system=SYSTEM,
            messages=[{"role": "user", "content": ticket}],
        )
        try:
            label = response_text(check_stop(response)).strip().lower()
        except UnusableResponse:
            label = ""  # truncated or refused: not a training example
        if label not in LABELS:
            skipped += 1
            continue  # keep only outputs that pass a check
        example = {"messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": ticket},
            {"role": "assistant", "content": label},
        ]}
        out.write(json.dumps(example) + "\n")
        kept += 1

print(f"kept {kept}, skipped {skipped}")
