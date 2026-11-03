# Generated from src/content/chapters (chapter 3) by `npm run labs`. Edit the chapter, not this file.
"""Run a prompt over a few test cases and print a pass rate."""
import anthropic

from llm_utils import UnusableResponse, check_stop, response_text

client = anthropic.Anthropic()

# Each case pairs an input with the word a good answer must contain.
CASES = [
    {"input": "I was charged twice for March.", "expect": "billing"},
    {"input": "The export button does nothing in Safari.", "expect": "bug"},
    {"input": "Could you add dark mode?", "expect": "feature_request"},
    {"input": "Do you have an office in Leeds?", "expect": "other"},
]


def run_baseline(make_prompt, cases=CASES, model="claude-opus-5-5"):
    passed = 0
    for case in cases:
        try:
            response = client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[{"role": "user", "content": make_prompt(case["input"])}],
            )
            output = response_text(check_stop(response)).strip().lower()
            ok = case["expect"] in output
        except UnusableResponse as e:
            output, ok = f"<unusable: {e}>", False  # a failure, not a crash
        passed += ok
        print("PASS" if ok else "FAIL", case["input"][:40], "->", output[:40])
    print(f"Pass rate: {passed}/{len(cases)} = {passed / len(cases):.0%}")
    return passed / len(cases)
