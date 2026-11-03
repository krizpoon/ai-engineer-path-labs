# Generated from src/content/chapters (chapter 12) by `npm run labs`. Edit the chapter, not this file.
from dataclasses import dataclass

import pytest

from evals.graders import grade_case

@dataclass
class Citation:
    doc_id: str
    quote: str

@dataclass
class Answer:
    text: str
    citations: list
    retrieved_ids: list
    abstained: bool

@dataclass
class Verdict:  # shaped like chapter 9's Verdict
    score: int

    @property
    def passed(self) -> bool:
        return self.score >= 4

CASE = {"id": "refund", "answerable": True,
        "must_include": ["30 days"], "relevant_ids": ["policy#0"]}
GOOD = Answer("Refunds are available within 30 days.",
              [Citation("policy#0", "Refunds are available within 30 days")],
              ["policy#0", "faq#2"], abstained=False)

def test_supported_answer_passes():
    checks = grade_case(CASE, GOOD, lambda answer, quotes: True)
    assert all(checks.values())

def test_unsupported_answer_fails():
    checks = grade_case(CASE, GOOD, lambda answer, quotes: False)
    assert checks["supported"] is False

def test_citing_an_unretrieved_passage_fails():
    bad = Answer(GOOD.text, [Citation("secret#0", "...")],
                 ["policy#0"], abstained=False)
    checks = grade_case(CASE, bad, lambda answer, quotes: True)
    assert checks["sources_valid"] is False

def test_a_judge_returning_a_verdict_is_rejected():
    # Verdict(score=1).passed is False, but the object itself is truthy.
    with pytest.raises(TypeError):
        grade_case(CASE, GOOD, lambda answer, quotes: Verdict(score=1))
