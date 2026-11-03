# Generated from src/content/chapters (chapter 5) by `npm run labs`. Edit the chapter, not this file.
import json
import anthropic
from llm_utils import check_stop, response_text
from order_tools import tools

client = anthropic.Anthropic()
MAX_STEPS = 10   # hard limit on model calls for one question

def get_order_status(order_id: str) -> dict:
    # Pretend this queries your database.
    if order_id != "1182":
        raise ValueError(f"No order with id {order_id}")
    return {"status": "in transit", "carrier": "DHL", "eta": "2026-10-28"}

TOOL_FUNCTIONS = {"get_order_status": get_order_status}

messages = [{"role": "user", "content": "Where is order 1182, and where is order 9999?"}]

for step in range(MAX_STEPS):
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        tools=tools,
        messages=messages,
    )
    # Raises on max_tokens, refusal and anything unexpected.
    check_stop(response, expected=("end_turn", "tool_use"))
    if response.stop_reason == "end_turn":
        break

    # Keep the assistant turn exactly as returned, tool_use blocks included.
    messages.append({"role": "assistant", "content": response.content})

    results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        try:
            output = TOOL_FUNCTIONS[block.name](**block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(output),
            })
        except Exception as e:
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": f"Error: {e}",
                "is_error": True,
            })

    # All results go back together, in a single user message.
    messages.append({"role": "user", "content": results})
else:
    raise RuntimeError(f"No answer after {MAX_STEPS} steps")

print(response_text(response))
