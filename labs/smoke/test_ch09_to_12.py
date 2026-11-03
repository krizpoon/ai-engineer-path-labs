"""Chapters 9–12: evals and judges, model comparison, reliability, the capstone gate."""
import json
import os
import shutil

import pytest

from conftest import LIVE, has, needs_ml, offline_only
from fake_claude import text, user_text

TICKETS = {json.loads(line)["input"]: json.loads(line)["expected"]
           for line in open(os.path.join(os.path.dirname(__file__), "..",
                                         "ch09-evaluation", "tickets.jsonl"))}


@offline_only
def test_ch09_eval_classifier_reports_by_tag(lab):
    def reply(request):  # right on everything except the mixed, angry ticket
        ticket = request["messages"][0]["content"]
        return text("bug" if "crashed" in ticket else TICKETS.get(ticket, "unknown"))
    out = lab(9).run("eval_classifier.py", reply=reply).stdout
    assert "Overall: 5/6 passed" in out
    assert "t05: expected 'billing', got 'bug'" in out


def steered(answer):
    return any(s in answer for s in ("no questions asked", "Grader:", "60 days", "shipping"))


def score(request):
    """Stand-in judge: low scores for replies a careful person failed."""
    graded = user_text(request).split("<reply>")[-1].split("<answer>")[-1]
    value = 1 if steered(graded) else 5
    return text(json.dumps({"justification": "Checked against the rubric.", "score": value}))


@offline_only
def test_ch09_judge_agrees_with_the_labels(lab):
    out = lab(9).run("judge.py", reply=score).stdout.splitlines()
    assert len(out) == 3 and all(line.startswith("ok:") for line in out)


def test_ch09_stats(lab):
    out = lab(9).run("-c", "from stats import compare, wilson_interval\n"
                     "low, high = wilson_interval(20, 20); print(f'{low:.2f} {high:.2f}')\n"
                     "old = {str(i): False for i in range(6)}\n"
                     "print(f'{compare(old, {k: True for k in old}):.3f}')").stdout
    assert out.splitlines()[0] == "0.84 1.00" and out.splitlines()[-1] == "0.031"


@offline_only
def test_ch10_compare_models(lab):
    ch10 = lab(10)
    out = ch10.run("compare_models.py", reply=lambda r: text("billing")).stdout
    assert len(out.splitlines()) == 3 and all(l.endswith("billing") for l in out.splitlines())
    assert [r["model"] for r in ch10.fake.requests] == \
        ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]


@offline_only
def test_ch10_distill_keeps_only_valid_labels(lab):
    ch10 = lab(10)
    ch10.add("ch10/tickets.txt")
    labels = {"charged": "billing", "blank": "bug", "export": "feature", "billed": "Billing!"}
    def reply(request):
        ticket = request["messages"][0]["content"]
        return text(next(v for k, v in labels.items() if k in ticket))
    assert ch10.run("distill.py", reply=reply).stdout.strip() == "kept 3, skipped 1"
    lines = (ch10.dir / "train.jsonl").read_text().splitlines()
    assert [json.loads(l)["messages"][2]["content"] for l in lines] == ["billing", "bug", "feature"]


HEAVY = pytest.mark.skipif(
    os.environ.get("LAB_HEAVY") != "1" or not has("peft", "torch", "transformers"),
    reason="set LAB_HEAVY=1 to download Qwen2.5-0.5B (about 1 GB) and run it on CPU")

UNTRAINED_ADAPTER = """
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM
base = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
lora = LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "v_proj"],
                  task_type="CAUSAL_LM")
get_peft_model(base, lora).save_pretrained("ticket-classifier-lora")
"""


@offline_only
@HEAVY
def test_ch10_finetuned_model_loads_and_compares(lab):
    """An untrained adapter: checks loading, inference and the comparison, not quality."""
    ch10 = lab(10)
    ch10.add("ch10/test.jsonl")
    ch10.run("-c", UNTRAINED_ADAPTER, timeout=900)
    reply = ch10.run("finetuned_model.py", timeout=900).stdout.strip()
    assert reply  # some text came back from the local model
    out = ch10.run("compare_baseline.py", reply=lambda r: text("billing"), timeout=900).stdout
    assert "Prompted baseline: 1/3" in out and "Fine-tuned model:" in out and "sign test p =" in out


def test_ch10_leak_guard(lab):
    ch10 = lab(10)
    leaked = '{"id": "x01", "input": "I was charged twice for my March invoice.", "label": "billing"}\n'
    (ch10.dir / "test.jsonl").write_text(leaked)
    (ch10.dir / "finetuned_model.py").write_text(  # never reached: the guard stops first
        "SYSTEM = ''\ndef finetuned_model(ticket):\n    raise AssertionError\n")
    result = ch10.run("compare_baseline.py", check=False)
    assert result.returncode != 0 and "also in training data: ['x01']" in result.stderr


def test_ch11_reliable_unit_tests(lab):
    lab(11).run("-m", "pytest", "-q", "-p", "no:cacheprovider", "test_reliable.py")


@offline_only
def test_ch11_falls_back_after_the_sdk_retries(lab):
    ch11 = lab(11)
    def reply(request):
        if request["model"] == "claude-opus-5-5":
            return {"status": 529, "error": "overloaded_error"}
        return text("Two incidents today.")
    out = ch11.run("-c", "from reliable import answer, client\n"
                   "from llm_utils import response_text\n"
                   "r = answer(client, [{'role': 'user', 'content': 'Incidents?'}])\n"
                   "print(response_text(r))", reply=reply, timeout=120).stdout
    assert out.strip() == "Two incidents today."
    models = [r["model"] for r in ch11.fake.requests]
    assert models == ["claude-opus-5-5"] * 4 + ["claude-sonnet-5-5"]  # 1 try + 3 retries


def test_ch12_gate_and_grader_unit_tests(lab):
    lab(12).run("-m", "pytest", "-q", "-p", "no:cacheprovider", "tests")


@offline_only
def test_ch12_judge_checks(lab):
    out = lab(12).run("evals/judge_checks.py", reply=score).stdout.splitlines()
    assert len(out) == 4 and all(line.startswith("ok:") for line in out)


def capstone(request):
    """Answers with a citation when a refunds passage was sent, else abstains."""
    if (request.get("output_config") or {}).get("format"):
        return score(request)  # the support judge
    blocks = request["messages"][0]["content"]
    docs = [b for b in blocks if b.get("type") == "document"]
    question = blocks[-1]["text"]
    for i, doc in enumerate(docs):
        if "refund" in question and "30 days" in doc["source"]["data"]:
            quote = "Customers can ask for a refund within 30 days of purchase."
            return text("Customers have 30 days to ask for a refund.", citations=[{
                "type": "char_location", "cited_text": quote, "document_index": i,
                "document_title": doc["title"], "start_char_index": 0,
                "end_char_index": len(quote)}])
    return text("I don't know. The documents I can see don't answer that.")


@offline_only
@needs_ml
def test_ch12_capstone_end_to_end(lab):
    ch12 = lab(12)
    ch12.add("ch12/handbook")
    assert "chunks indexed" in ch12.run("-m", "docs_assistant.ingest").stdout

    first = ch12.run("-m", "evals.run_evals", reply=capstone, check=False)
    assert "3/3 passed" in first.stdout and "No evals/baseline.json" in first.stderr
    results = json.loads((ch12.dir / "evals/results.json").read_text())
    assert results["cases"]["refund-window"]["checks"]["cites_relevant"] is True
    # The managers-only salary passage never reached the model for a staff user.
    assert not any("pay committee" in json.dumps(r) for r in ch12.fake.requests)

    shutil.copy(ch12.dir / "evals/results.json", ch12.dir / "evals/baseline.json")
    assert "3/3 passed" in ch12.run("-m", "evals.run_evals", reply=capstone).stdout

    cases = ch12.dir / "evals/cases.jsonl"  # drop the critical case: the gate must fail
    cases.write_text("\n".join(l for l in cases.read_text().splitlines()
                               if "acl-salaries" not in l) + "\n")
    dropped = ch12.run("-m", "evals.run_evals", reply=capstone, check=False)
    assert dropped.returncode != 0 and "baseline cases missing from this run: ['acl-salaries']" \
        in dropped.stderr
