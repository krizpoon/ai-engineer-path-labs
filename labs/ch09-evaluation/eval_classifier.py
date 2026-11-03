# Generated from src/content/chapters (chapter 9) by `npm run labs`. Edit the chapter, not this file.
import json
from collections import defaultdict
import anthropic
from llm_utils import check_stop, response_text, UnusableResponse

client = anthropic.Anthropic()

SYSTEM_V1 = """You label customer support tickets.
Reply with exactly one word: billing, bug, feature_request, account or unknown."""

def classify(ticket: str, system: str) -> str:
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=2000,
        system=system,
        output_config={"effort": "low"},  # simple task: keep it fast and cheap
        messages=[{"role": "user", "content": ticket or "(empty ticket)"}],
    )
    check_stop(response)  # raises UnusableResponse unless end_turn
    return response_text(response).strip().lower()

def run_eval(system: str, path: str = "tickets.jsonl") -> dict[str, bool]:
    with open(path) as f:
        cases = [json.loads(line) for line in f if line.strip()]
    if not cases:
        raise ValueError(f"{path} has no test cases")

    results = {}  # case id -> passed: keep these to compare versions
    by_tag = defaultdict(lambda: [0, 0])  # tag -> [passed, total]
    failures = []
    for case in cases:
        try:
            got = classify(case["input"], system)
        except UnusableResponse as err:
            got = f"<unusable: {err}>"
        passed = got == case["expected"]
        results[case["id"]] = passed
        for tag in case["tags"]:
            by_tag[tag][0] += passed
            by_tag[tag][1] += 1
        if not passed:
            failures.append(f"{case['id']}: expected {case['expected']!r}, got {got!r}")

    print(f"Overall: {sum(results.values())}/{len(cases)} passed")
    for tag, (p, t) in sorted(by_tag.items()):
        print(f"  {tag:<10} {p}/{t}")
    print("Failures:", *failures, sep="\n  ")
    return results

if __name__ == "__main__":
    run_eval(SYSTEM_V1)
