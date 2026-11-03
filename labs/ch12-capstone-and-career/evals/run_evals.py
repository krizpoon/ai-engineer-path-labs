# Generated from src/content/chapters (chapter 12) by `npm run labs`. Edit the chapter, not this file.
import hashlib
import json
import sys
from pathlib import Path

from docs_assistant.rag import answer_question
from evals.gate import case_hash, check_suite, gate
from evals.graders import grade_case
from evals.judges import support_judge
from evals.users import user_for

CASES = Path("evals/cases.jsonl")
# Ordinary cases deliberately removed in this pull request. Any other
# missing baseline case fails the gate; critical ones cannot be retired.
RETIRED: set[str] = set()

cases = [json.loads(line) for line in CASES.read_text().splitlines()
         if line.strip()]
check_suite(cases)  # empty or duplicate ids: stop before spending

results = {}
for case in cases:
    answer = answer_question(case["question"], user_for(case["groups"]))
    checks = grade_case(case, answer, support_judge)
    results[case["id"]] = {"passed": all(checks.values()),
                           "critical": case["critical"],
                           "hash": case_hash(case), "checks": checks}
current = {
    "dataset_version": hashlib.sha256(CASES.read_bytes()).hexdigest()[:12],
    "cases": results,
}
# Keep every case's result; on main, CI saves this as baseline.json.
Path("evals/results.json").write_text(json.dumps(current, indent=2))

passes = sum(r["passed"] for r in results.values())
print(f"{passes}/{len(results)} passed")
BASELINE = Path("evals/baseline.json")
if not BASELINE.exists():  # first run: nothing to compare with yet
    sys.exit(f"No {BASELINE}: review evals/results.json, then commit it "
             "as the baseline.")
baseline = json.loads(BASELINE.read_text())
failures = gate(baseline, current, RETIRED)
if failures:
    sys.exit("FAIL:\n- " + "\n- ".join(failures))
