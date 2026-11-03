# Generated from src/content/chapters (chapter 11) by `npm run labs`. Edit the chapter, not this file.
import anthropic

from llm_utils import check_stop

PRIMARY = "claude-opus-5-5"
FALLBACK = "claude-sonnet-5-5"

# Retries 429, 5xx and connection errors with backoff before raising.
client = anthropic.Anthropic(timeout=30.0, max_retries=3)

def answer(client, messages):
    """Primary model first; fall back on outages, rate limits,
    timeouts and refusals."""
    try:
        response = client.messages.create(
            model=PRIMARY, max_tokens=2000, messages=messages
        )
    except anthropic.APIStatusError as e:
        if e.status_code != 429 and e.status_code < 500:
            raise  # 400, 401, 404: our request is wrong; don't hide it
        response = None  # 429 or 5xx, after the SDK's own retries
    except anthropic.APIConnectionError:  # includes timeouts
        response = None

    if response is None or response.stop_reason == "refusal":
        response = client.messages.create(
            model=FALLBACK, max_tokens=2000, messages=messages
        )
    # Truncation raises UnusableResponse: a cut-off answer is not an answer.
    return check_stop(response)
