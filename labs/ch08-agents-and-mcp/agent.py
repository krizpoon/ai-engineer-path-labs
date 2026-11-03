# Generated from src/content/chapters (chapter 8) by `npm run labs`. Edit the chapter, not this file.
import difflib
import json
import time

import anthropic

from llm_utils import check_stop, response_text
from tools import execute_tool, safe_path

# No automatic retries, so each call's timeout bounds the whole call
client = anthropic.Anthropic(max_retries=0)

TOOLS = [
    {
        "name": "read_file",
        "description": (
            "Read one UTF-8 text file inside the project. Paths are relative "
            "to the project root. Files outside the project, likely secrets "
            "(.env, keys, .git) and files over 100 KB are refused."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": (
            "Replace a text file inside the project. A person must approve "
            "every write; the same path rules as read_file apply."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_tests",
        "description": (
            "Run the project's pytest suite without credentials, with a "
            "120-second timeout. Returns the last 6,000 characters of output."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]

NEEDS_APPROVAL = {"write_file"}
MODEL = "claude-opus-5-5"
MAX_TOKENS = 8000
MAX_STEPS = 10
MAX_SECONDS = 300
MAX_COST = 2.00  # US dollars
# Claude Opus 5.5 list prices per token (checked October 2026)
PRICE_IN, PRICE_OUT = 4 / 1_000_000, 20 / 1_000_000


def approved(name: str, args: dict) -> bool:
    if name == "write_file":
        # Show the whole change: you are about to run this code as yourself
        path = safe_path(args["path"], must_exist=False)
        old = path.read_text() if path.is_file() else ""
        print("".join(difflib.unified_diff(
            old.splitlines(keepends=True),
            args["content"].splitlines(keepends=True),
            args["path"], args["path"] + " (proposed)")))
    else:
        print(f"Agent wants {name}({json.dumps(args)[:500]})")
    return input("Allow? [y/N] ").strip().lower() == "y"


def run_tool_call(block, seconds_left: float) -> dict:
    result = {"type": "tool_result", "tool_use_id": block.id}
    try:
        if block.name in NEEDS_APPROVAL and not approved(block.name, block.input):
            return result | {"content": "The user declined.", "is_error": True}
        content = execute_tool(block.name, block.input, seconds_left)
        return result | {"content": content}
    except Exception as e:  # ToolDenied, timeouts, bad paths...
        # Report failures to the model instead of crashing; it can adapt
        return result | {"content": f"Error: {e}", "is_error": True}


TASK = "The tests are failing. Find the cause, fix it, and re-run the tests."
messages = [{"role": "user", "content": TASK}]
deadline, spent = time.monotonic() + MAX_SECONDS, 0.0

for step in range(MAX_STEPS):
    # Reserve the worst case before calling: the exact input plus a
    # full-length reply. Counting tokens is free but takes a request.
    input_tokens = client.messages.count_tokens(
        model=MODEL, tools=TOOLS, messages=messages).input_tokens
    worst_case = input_tokens * PRICE_IN + MAX_TOKENS * PRICE_OUT
    seconds_left = deadline - time.monotonic()
    if spent + worst_case > MAX_COST or seconds_left <= 0:
        print(f"Stopped at step {step}: {spent:.2f} USD spent, "
              f"{max(seconds_left, 0):.0f}s left")
        break
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        tools=TOOLS,
        messages=messages,
        timeout=seconds_left,  # the call cannot run past the deadline
    )
    usage = response.usage
    spent += usage.input_tokens * PRICE_IN + usage.output_tokens * PRICE_OUT
    # Truncated or refused replies raise here instead of passing as answers
    check_stop(response, expected=("end_turn", "tool_use"))
    # Keep every block (text, thinking, tool_use) in the history
    messages.append({"role": "assistant", "content": response.content})
    if response.stop_reason == "end_turn":
        print(response_text(response))
        break
    # Every tool_use gets a result, and all go back in one user message
    results = [run_tool_call(b, deadline - time.monotonic())
               for b in response.content if b.type == "tool_use"]
    messages.append({"role": "user", "content": results})
else:
    print(f"Stopped: no answer after {MAX_STEPS} steps ({spent:.2f} USD)")
