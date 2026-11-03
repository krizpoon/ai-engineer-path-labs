# Generated from src/content/chapters (chapter 11) by `npm run labs`. Edit the chapter, not this file.
from types import SimpleNamespace

import anthropic
import pytest

from llm_utils import UnusableResponse
from reliable import FALLBACK, PRIMARY, answer

def fake_error(cls, status=None):
    """An SDK exception built without a network call.
    answer() only reads status_code."""
    error = cls.__new__(cls)
    Exception.__init__(error, f"simulated {cls.__name__}")
    error.status_code = status
    return error

def reply(stop_reason):
    return SimpleNamespace(
        stop_reason=stop_reason, stop_details=None,
        content=[SimpleNamespace(type="text", text="ok")],
    )

class FakeClient:
    """Plays back scripted outcomes: a reply to return or an error to raise."""
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.models = []
        self.messages = self  # client.messages.create(...) lands below

    def create(self, *, model, **params):
        self.models.append(model)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

MSG = [{"role": "user", "content": "Summarise today's incidents."}]

@pytest.mark.parametrize("failure", [
    fake_error(anthropic.InternalServerError, 500),
    fake_error(anthropic.RateLimitError, 429),
    fake_error(anthropic.APITimeoutError),
    reply("refusal"),
])
def test_falls_back(failure):
    client = FakeClient(failure, reply("end_turn"))
    assert answer(client, MSG).stop_reason == "end_turn"
    assert client.models == [PRIMARY, FALLBACK]

def test_truncation_is_an_error_not_an_answer():
    client = FakeClient(reply("max_tokens"))
    with pytest.raises(UnusableResponse):
        answer(client, MSG)

def test_bad_request_is_not_hidden_by_the_fallback():
    client = FakeClient(fake_error(anthropic.NotFoundError, 404))
    with pytest.raises(anthropic.NotFoundError):
        answer(client, MSG)
    assert client.models == [PRIMARY]
