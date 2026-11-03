"""A local stand-in for the Claude Messages API, for offline smoke tests.

The lab scripts use the real `anthropic` SDK; the smoke tests point it here with
ANTHROPIC_BASE_URL, so requests, parsing, tool runners and errors behave as they
would against the API, without a key or any network traffic. A test supplies a
`reply(request) -> dict` function that decides each response.
"""
import itertools
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_ids = itertools.count(1)


def text(body, stop_reason="end_turn", citations=None):
    block = {"type": "text", "text": body}
    if citations is not None:
        block["citations"] = citations
    return {"content": [block], "stop_reason": stop_reason}


def tool_use(name, args, *more):
    """One reply asking for one or more tools: tool_use(name, args, name2, args2)."""
    pairs = [(name, args), *zip(more[::2], more[1::2])]
    return {
        "content": [{"type": "tool_use", "id": f"toolu_{next(_ids):04d}", "name": n, "input": a}
                    for n, a in pairs],
        "stop_reason": "tool_use",
    }


def refusal():
    return {"content": [], "stop_reason": "refusal",
            "stop_details": {"type": "refusal", "category": "cyber"}}


def from_schema(schema, defs=None):
    """A minimal instance of a JSON schema: enough for structured-output parsing."""
    defs = defs or schema.get("$defs", {})
    if "$ref" in schema:
        return from_schema(defs[schema["$ref"].split("/")[-1]], defs)
    for key in ("anyOf", "oneOf", "allOf"):
        if key in schema:
            return from_schema(schema[key][0], defs)
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][-1]
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = kind[0]
    if kind == "object":
        return {k: from_schema(v, defs) for k, v in schema.get("properties", {}).items()}
    return {"array": [], "string": "x", "integer": 5, "number": 5.0,
            "boolean": True, "null": None}.get(kind, "x")


def tool_results(request):
    """The tool_result blocks in the latest user turn, if any."""
    last = request["messages"][-1]
    content = last["content"] if isinstance(last["content"], list) else []
    return [b for b in content if isinstance(b, dict) and b.get("type") == "tool_result"]


def user_text(request):
    """All plain text the user has sent, for keyword-based fake replies."""
    parts = []
    for message in request["messages"]:
        if message["role"] != "user":
            continue
        content = message["content"]
        if isinstance(content, str):
            parts.append(content)
        else:
            parts += [b.get("text", "") for b in content if isinstance(b, dict)]
    return "\n".join(parts)


def default_reply(request):
    """Structured output gets a schema-shaped JSON reply; anything else gets text."""
    fmt = (request.get("output_config") or {}).get("format")
    if fmt and fmt.get("type") == "json_schema":
        return text(json.dumps(from_schema(fmt["schema"])))
    return text("OK")


class FakeClaude:
    """Runs on 127.0.0.1 in a thread; `requests` records every request body."""

    def __init__(self, reply=default_reply):
        self.reply = reply
        self.requests = []  # full request bodies, thread history included
        self.paths = []
        self.threads = {}  # last message id -> the conversation so far
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["content-length"])))
                fake.paths.append(self.path.split("?")[0])
                if self.path.startswith("/v1/messages/count_tokens"):
                    return self.send({"input_tokens": len(json.dumps(body)) // 4})
                # The SDK's Tool Runner keeps history on the server: a request may
                # create a thread or continue one, sending only the new messages.
                thread = body.get("thread") or {}
                if thread.get("type") == "continue":
                    earlier = fake.threads[thread["previous_message_id"]]
                    body = body | {"messages": earlier + body["messages"]}
                fake.requests.append(body)
                if body.get("stream"):
                    return self.send({"type": "error", "error": {
                        "type": "invalid_request_error",
                        "message": "the fake server does not stream"}}, 400)
                outcome = fake.reply(body)
                if "status" in outcome:  # simulate an API error
                    return self.send({"type": "error", "error": {
                        "type": outcome.get("error", "api_error"),
                        "message": "simulated"}}, outcome["status"])
                message_id = f"msg_fake_{next(_ids):04d}"
                if thread:
                    fake.threads[message_id] = body["messages"] + [
                        {"role": "assistant", "content": outcome["content"]}]
                self.send({
                    "id": message_id, "type": "message",
                    "role": "assistant", "model": body["model"],
                    "content": outcome["content"],
                    "stop_reason": outcome["stop_reason"],
                    "stop_sequence": None,
                    "stop_details": outcome.get("stop_details"),
                    "usage": {"input_tokens": 100, "output_tokens": 20},
                })

            def send(self, payload, status=200):
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(data)))
                self.send_header("request-id", f"req_fake_{next(_ids):04d}")
                self.end_headers()
                self.wfile.write(data)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
