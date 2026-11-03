# Generated from src/content/chapters (chapter 5) by `npm run labs`. Edit the chapter, not this file.
import anthropic
from anthropic import beta_tool
from llm_utils import check_stop, response_text

client = anthropic.Anthropic()
MAX_STEPS = 10

@beta_tool
def get_order_status(order_id: str) -> str:
    """Look up the current shipping status of a customer order.

    Args:
        order_id: Order number, e.g. "1182".
    """
    return '{"status": "in transit", "carrier": "DHL", "eta": "2026-10-28"}'

runner = client.beta.messages.tool_runner(
    model="claude-opus-5-5",
    max_tokens=4000,
    max_iterations=MAX_STEPS,  # at most 10 model replies
    tools=[get_order_status],
    messages=[{"role": "user", "content": "Where is order 1182?"}],
)

# One message per model reply; the runner runs requested tools in between.
for message in runner:
    if message.stop_reason == "tool_use":
        continue  # not an answer yet
    check_stop(message)  # refusal, max_tokens... raise before anything is shown
    print(response_text(message))
    break
else:
    # max_iterations ran out while the model was still asking for tools
    raise RuntimeError(f"No answer within {MAX_STEPS} model replies")
