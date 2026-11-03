# Generated from src/content/chapters (chapter 3) by `npm run labs`. Edit the chapter, not this file.
"""Small helpers that the rest of the course imports."""


class UnusableResponse(Exception):
    """The model stopped for a reason the caller did not plan for."""


def check_stop(response, expected=("end_turn",)):
    """Return the response if it stopped for an expected reason, else raise."""
    reason = response.stop_reason
    if reason in expected:
        return response
    if reason == "max_tokens":
        raise UnusableResponse("Cut off at max_tokens: raise the limit or ask for less.")
    if reason == "model_context_window_exceeded":
        raise UnusableResponse("Context window full: trim the history or the input.")
    if reason == "refusal":
        details = response.stop_details
        category = getattr(details, "category", None) or "unknown"
        raise UnusableResponse(f"Refused (category: {category}). Not an answer.")
    raise UnusableResponse(f"Unexpected stop_reason: {reason!r}")


def response_text(response) -> str:
    """Join the text blocks, skipping thinking and tool_use blocks."""
    return "".join(b.text for b in response.content if b.type == "text")
