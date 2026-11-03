# Generated from src/content/chapters (chapter 3) by `npm run labs`. Edit the chapter, not this file.
from types import SimpleNamespace as Fake

from llm_utils import UnusableResponse, check_stop, response_text


def fake(stop_reason, text="", category=None):
    """A stand-in for a real response: same attributes, no API call."""
    details = Fake(category=category) if stop_reason == "refusal" else None
    return Fake(stop_reason=stop_reason, stop_details=details,
                content=[Fake(type="thinking", thinking=""),
                         Fake(type="text", text=text)])


assert response_text(check_stop(fake("end_turn", "Hi"))) == "Hi"
assert check_stop(fake("tool_use"), expected=("end_turn", "tool_use"))

for reason in ["max_tokens", "refusal", "model_context_window_exceeded", "pause_turn"]:
    try:
        check_stop(fake(reason, category="cyber"))
    except UnusableResponse as e:
        print(f"{reason}: {e}")
    else:
        raise AssertionError(f"{reason} should have raised")

print("All fixtures behave as expected.")
