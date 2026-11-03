# Generated from src/content/chapters (chapter 12) by `npm run labs`. Edit the chapter, not this file.
import pytest

from evals.gate import check_suite, gate

def run(version: str, **cases) -> dict:
    """run("v1", refund=(True, False)): id=(passed, critical)."""
    return {"dataset_version": version, "cases": {
        i: {"passed": p, "critical": c, "hash": i}
        for i, (p, c) in cases.items()}}

MAIN = run("v1", acl_hr=(True, True), refund=(True, False))

def test_normal_run_passes():
    assert gate(MAIN, run("v1", acl_hr=(True, True),
                          refund=(True, False)), set()) == []

def test_empty_run_fails():
    assert gate(MAIN, run("v1"), set()) == ["no cases ran"]

def test_missing_critical_case_fails():
    reasons = gate(MAIN, run("v2", refund=(True, False)), set())
    assert any("missing" in r for r in reasons)

def test_critical_case_cannot_be_retired():
    reasons = gate(MAIN, run("v2", refund=(True, False)), {"acl_hr"})
    assert any("cannot be retired" in r for r in reasons)

def test_listed_ordinary_case_can_be_retired():
    assert gate(MAIN, run("v2", acl_hr=(True, True)), {"refund"}) == []

def test_dropping_the_critical_flag_does_not_hide_a_failure():
    reasons = gate(MAIN, run("v1", acl_hr=(False, False),
                             refund=(True, False)), set())
    assert any("critical cases failed" in r for r in reasons)

def test_empty_and_duplicate_suites_are_rejected():
    with pytest.raises(ValueError):
        check_suite([])
    with pytest.raises(ValueError):
        check_suite([{"id": "a"}, {"id": "a"}])
