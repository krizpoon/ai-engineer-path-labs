# Generated from src/content/chapters (chapter 5) by `npm run labs`. Edit the chapter, not this file.
import json
import anthropic
from llm_utils import check_stop, response_text

client = anthropic.Anthropic()
email = "Order 1182 arrived with a cracked mug. I need it before Saturday!"

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": f"Classify this ticket:\n\n{email}"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["refund", "delivery", "bug", "other"]},
                    "urgent": {"type": "boolean"},
                },
                "required": ["category", "urgent"],
                "additionalProperties": False,
            },
        }
    },
)

check_stop(response)   # never parse a truncated or refused reply
data = json.loads(response_text(response))
print(data["category"], data["urgent"])
