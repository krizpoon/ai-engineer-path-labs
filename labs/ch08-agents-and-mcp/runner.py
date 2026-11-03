# Generated from src/content/chapters (chapter 8) by `npm run labs`. Edit the chapter, not this file.
import anthropic
from anthropic import beta_tool

from llm_utils import check_stop, response_text
from tools import safe_path

client = anthropic.Anthropic()
MAX_STEPS = 10
MAX_COST = 0.50  # US dollars, checked between replies
PRICE_IN, PRICE_OUT = 4 / 1_000_000, 20 / 1_000_000  # Opus 5.5, Oct 2026


@beta_tool
def read_file(path: str) -> str:
    """Read one UTF-8 text file inside the project.

    Files outside the project, likely secrets (.env, keys, .git) and
    files over 100 KB are refused.

    Args:
        path: Path relative to the project root.
    """
    return safe_path(path).read_text()  # ToolDenied becomes an error result


runner = client.beta.messages.tool_runner(
    model="claude-opus-5-5",
    max_tokens=16000,
    max_iterations=MAX_STEPS,
    tools=[read_file],
    messages=[{"role": "user", "content": "Explain what shop/pricing.py does."}],
)

spent = 0.0
for message in runner:  # one message per model reply
    spent += (message.usage.input_tokens * PRICE_IN
              + message.usage.output_tokens * PRICE_OUT)
    # Refused or truncated replies raise before anything is shown
    check_stop(message, expected=("end_turn", "tool_use"))
    if message.stop_reason == "end_turn":
        print(response_text(message))
        break
    if spent > MAX_COST:
        print(f"Stopped: {spent:.2f} USD spent")
        break
else:
    print(f"Stopped: no answer within {MAX_STEPS} replies ({spent:.2f} USD)")
