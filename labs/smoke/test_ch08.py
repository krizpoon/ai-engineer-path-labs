"""Chapter 8: chains, the file-fixing agent, the Tool Runner and MCP.

The agent runs the real tools on the disposable fixture project, including a real
pytest run; only the model's decisions are scripted.
"""
from conftest import has, offline_only
from fake_claude import text, tool_results, tool_use

import pytest

FIXED = '''def apply_discount(price: float, percent: float) -> float:
    """Return the price after a percentage discount."""
    return price * (1 - percent / 100)
'''


def fixture_project(lab):
    ch8 = lab(8)
    ch8.run("-c", "import subprocess; subprocess.run(['bash', 'make_fixture.sh'], check=True)")
    return ch8


def test_ch08_path_guard(lab):
    out = fixture_project(lab).run("check_guard.py").stdout.splitlines()
    assert [line.split(":")[0] for line in out] == ["refused"] * 4 + ["allowed"]


@offline_only
def test_ch08_chain_checks_the_outline(lab):
    def reply(request):
        prompt = request["messages"][0]["content"]
        return text("\n".join(f"{i}. Point" for i in range(1, 6))) if "outline" in prompt \
            and "Follow this" not in prompt else text("The finished post.")
    assert lab(8).run("chain.py", reply=reply).stdout.strip() == "The finished post."

    bad = lab(8).run("chain.py", reply=lambda r: text("1. Only one point"), check=False)
    assert bad.returncode != 0 and "Expected 5 outline points, got 1" in bad.stderr


def fixer(request):
    """Reads the code, probes the guard, proposes the fix, runs the tests, reports."""
    turn = sum(1 for m in request["messages"] if m["role"] == "assistant")
    steps = [
        tool_use("read_file", {"path": "shop/pricing.py"},
                 "read_file", {"path": "../outside.txt"},
                 "read_file", {"path": ".env"}),
        tool_use("write_file", {"path": "shop/pricing.py", "content": FIXED}),
        tool_use("run_tests", {}),
    ]
    return steps[turn] if turn < len(steps) else text("Fixed: percent is now a percentage.")


@offline_only
def test_ch08_agent_fixes_the_bug_with_approval(lab):
    ch8 = fixture_project(lab)
    out = ch8.run("agent.py", reply=fixer, stdin="y\n").stdout
    assert "+    return price * (1 - percent / 100)" in out  # the diff shown before approval
    assert out.strip().endswith("Fixed: percent is now a percentage.")

    read, write, tests = (tool_results(r) for r in ch8.fake.requests[1:4])
    assert [r.get("is_error", False) for r in read] == [False, True, True]
    assert "outside the project" in read[1]["content"] and "secrets" in read[2]["content"]
    assert "1 passed" in tests[0]["content"]
    assert (ch8.dir / "fixture-project/shop/pricing.py").read_text() == FIXED
    assert "/v1/messages/count_tokens" in ch8.fake.paths  # spend reserved before each call


@offline_only
def test_ch08_agent_write_refused_without_approval(lab):
    ch8 = fixture_project(lab)
    ch8.run("agent.py", reply=fixer, stdin="n\n")
    declined = tool_results(ch8.fake.requests[2])[0]
    assert declined["is_error"] and declined["content"] == "The user declined."
    assert "percent  # bug" in (ch8.dir / "fixture-project/shop/pricing.py").read_text()


@offline_only
def test_ch08_runner_reads_through_the_guard(lab):
    ch8 = fixture_project(lab)
    reply = lambda r: text("It subtracts the percentage.") if tool_results(r) \
        else tool_use("read_file", {"path": "shop/pricing.py"})
    assert ch8.run("runner.py", reply=reply).stdout.strip() == "It subtracts the percentage."
    assert "def apply_discount" in tool_results(ch8.fake.requests[1])[0]["content"]


@offline_only
@pytest.mark.skipif(not has("mcp"), reason="needs the mcp package")
def test_ch08_mcp_client_calls_the_docs_server(lab):
    ch8 = lab(8)
    reply = lambda r: text("Run make deploy-staging.") if tool_results(r) \
        else tool_use("search_docs", {"query": "staging"})
    assert ch8.run("mcp_client.py", reply=reply, timeout=120).stdout.strip() == \
        "Run make deploy-staging."
    assert "make deploy-staging" in str(tool_results(ch8.fake.requests[1])[0]["content"])
