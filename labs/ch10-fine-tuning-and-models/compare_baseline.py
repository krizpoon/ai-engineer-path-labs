# Generated from src/content/chapters (chapter 10) by `npm run labs`. Edit the chapter, not this file.
import json
import anthropic
from llm_utils import check_stop, response_text, UnusableResponse
from finetuned_model import SYSTEM, finetuned_model
from stats import compare, wilson_interval  # chapter 9

client = anthropic.Anthropic()

# Your best prompt: the same task, with definitions to help.
BASELINE_PROMPT = SYSTEM + """
billing: charges, invoices, refunds, payment methods.
bug: something in the product is broken or wrong.
feature: a request for something the product does not do."""

def prompted_baseline(ticket: str) -> str:
    response = client.messages.create(
        model="claude-haiku-5-5",  # the cheap model you would ship
        max_tokens=1000,
        output_config={"effort": "low"},
        system=BASELINE_PROMPT,
        messages=[{"role": "user", "content": ticket}],
    )
    try:
        return response_text(check_stop(response)).strip().lower()
    except UnusableResponse:
        return "<unusable>"  # counts as wrong

def run(predict, examples) -> dict[str, bool]:
    return {ex["id"]: predict(ex["input"]) == ex["label"]
            for ex in examples}

def load(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

# test.jsonl lines: {"id": "...", "input": "...", "label": "..."}
test_set = load("test.jsonl")
if not test_set:
    raise SystemExit("test.jsonl is empty")
trained = {ex["messages"][1]["content"] for ex in load("train.jsonl")}
leaked = [ex["id"] for ex in test_set if ex["input"] in trained]
if leaked:
    raise SystemExit(f"test cases also in training data: {leaked}")

base_results = run(prompted_baseline, test_set)
tuned_results = run(finetuned_model, test_set)

n = len(test_set)
for name, results in [("Prompted baseline", base_results),
                      ("Fine-tuned model", tuned_results)]:
    low, high = wilson_interval(sum(results.values()), n)
    print(f"{name}: {sum(results.values())}/{n} "
          f"(95% interval {low:.0%}-{high:.0%})")
p = compare(base_results, tuned_results)  # paired, same cases
print(f"sign test p = {p:.2f}")
