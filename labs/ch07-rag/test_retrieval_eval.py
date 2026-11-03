# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
import pytest
from retrieval_eval import score_retrieval

CASES = [
    {"question": "q1", "groups": ["everyone"], "evidence": ["Fact A."]},
    {"question": "q2", "groups": ["everyone"], "evidence": [],
     "restricted": ["Secret B."]},
]

def fixed(*texts):
    """A fake retriever that always returns these passages."""
    def retrieve(question, groups, k):
        return [{"id": str(i), "text": t, "source": "fake.md"}
                for i, t in enumerate(texts[:k])]
    return retrieve

def test_the_retriever_under_test_is_used():
    assert score_retrieval(CASES, fixed("Fact A."))["recall"] == 1.0
    assert score_retrieval(CASES, fixed("Other."))["recall"] == 0.0

def test_restricted_text_fails_the_run():
    with pytest.raises(AssertionError):
        score_retrieval(CASES, fixed("Fact A.", "Secret B."))
