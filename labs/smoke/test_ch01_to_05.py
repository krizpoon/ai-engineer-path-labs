"""Chapters 1–5: first calls, llm_utils, baselines, prompts, tools and structured output."""
import json
import re

from conftest import offline_only
from fake_claude import refusal, text, tool_results, tool_use, user_text


def test_ch01_hello(lab):
    out = lab(1).run("hello.py").stdout
    assert "end_turn" in out and "input_tokens" in out


def test_ch02_redact(lab):
    out = lab(2).run("redact.py").stdout
    assert out.strip() == "Jane ([email]) pasted [api_key] and card [card]."


def test_ch03_llm_utils_unit_tests(lab):
    out = lab(3).run("test_llm_utils.py").stdout
    assert "All fixtures behave as expected." in out


def label(request):
    """Keyword classifier standing in for the model; reads only the message to label."""
    sent = user_text(request)
    message = (re.findall(r"<message>(.*?)</message>", sent, re.S) or [sent])[-1].lower()
    for word, category in [("charged", "billing"), ("export", "bug"),
                           ("dark mode", "feature_request")]:
        if word in message:
            return category
    return "other"


@offline_only
def test_ch03_baseline(lab):
    out = lab(3).run("-c", "from baseline import run_baseline\n"
                     "run_baseline(lambda m: 'Classify: ' + m)",
                     reply=lambda r: text(label(r))).stdout
    assert "Pass rate: 4/4 = 100%" in out


@offline_only
def test_ch04_compare_prompts(lab):
    out = lab(4).run("compare_prompts.py",
                     reply=lambda r: text(f"<category>{label(r)}</category>")).stdout
    assert "v1: 1.0" in out and "v2: 1.0" in out


def test_ch04_prompt_template(lab):
    out = lab(4).run("-c", "from prompts.ticket_summary import VERSION, render\n"
                     "print(VERSION); print(render('Login fails', 'Pro'))").stdout
    assert "ticket-summary/v3" in out and "Login fails" in out and "plan: Pro." in out


TICKET = {"customer_name": "Jane Doe", "order_number": "1182", "category": "delivery",
          "urgent": True, "products": ["mug", "teapot"]}


@offline_only
def test_ch05_extract_ticket(lab):
    ch5 = lab(5)
    out = ch5.run("extract_ticket.py", reply=lambda r: text(json.dumps(TICKET))).stdout
    assert out.strip() == "1182 True ['mug', 'teapot']"
    assert ch5.fake.requests[0]["output_config"]["format"]["type"] == "json_schema"


def test_ch05_classify_ticket(lab):
    out = lab(5).run("classify_ticket.py").stdout
    category, urgent = out.split()
    assert category in {"refund", "delivery", "bug", "other"} and urgent in {"True", "False"}


def orders(request):
    if not tool_results(request):
        return tool_use("get_order_status", {"order_id": "1182"},
                        "get_order_status", {"order_id": "9999"})
    return text("1182 is in transit with DHL; 9999 does not exist.")


@offline_only
def test_ch05_order_loop_returns_all_results_together(lab):
    ch5 = lab(5)
    out = ch5.run("order_loop.py", reply=orders).stdout
    assert "in transit" in out
    results = ch5.fake.requests[1]["messages"][-1]["content"]
    assert len(results) == 2 and [r.get("is_error", False) for r in results] == [False, True]


def slow_answer(request):
    """Nine tool calls, then an answer on the tenth and last allowed reply."""
    calls = sum(1 for m in request["messages"] if m["role"] == "assistant")
    return tool_use("get_order_status", {"order_id": "1182"}) if calls < 9 else text("In transit.")


@offline_only
def test_ch05_runner_accepts_an_answer_on_the_last_turn(lab):
    ch5 = lab(5)
    out = ch5.run("order_runner.py", reply=slow_answer).stdout
    assert out.strip() == "In transit." and len(ch5.fake.requests) == 10


@offline_only
def test_ch05_runner_stops_at_its_limit(lab):
    result = lab(5).run("order_runner.py", check=False,
                        reply=lambda r: tool_use("get_order_status", {"order_id": "1182"}))
    assert result.returncode != 0 and "No answer within 10 model replies" in result.stderr


@offline_only
def test_ch05_runner_raises_on_refusal_before_printing(lab):
    result = lab(5).run("order_runner.py", check=False, reply=lambda r: refusal())
    assert result.returncode != 0 and result.stdout == ""
    assert "UnusableResponse" in result.stderr
