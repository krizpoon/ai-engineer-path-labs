# Generated from src/content/chapters (chapter 8) by `npm run labs`. Edit the chapter, not this file.
import os
import subprocess
import sys
from pathlib import Path

PROJECT = Path("fixture-project").resolve()  # the only directory the tools touch
MAX_FILE_BYTES = 100_000
SECRET_NAMES = {".git", ".ssh", "secrets"}
SECRET_SUFFIXES = {".pem", ".key", ".p12"}


class ToolDenied(Exception):
    pass


def safe_path(relative: str, must_exist: bool = True) -> Path:
    # resolve() collapses "..", follows symlinks, and an absolute path
    # replaces PROJECT entirely, so check where the path really points.
    path = (PROJECT / relative).resolve()
    if not path.is_relative_to(PROJECT):
        raise ToolDenied(f"{relative} is outside the project")
    parts = path.relative_to(PROJECT).parts
    if (any(p in SECRET_NAMES or p.startswith(".env") for p in parts)
            or path.suffix in SECRET_SUFFIXES):
        raise ToolDenied(f"{relative} may hold secrets")
    if must_exist and not path.is_file():
        raise ToolDenied(f"{relative} is not a file in the project")
    if must_exist and path.stat().st_size > MAX_FILE_BYTES:
        raise ToolDenied(f"{relative} is over {MAX_FILE_BYTES:,} bytes")
    return path


def run_tests(seconds: float = 120) -> str:
    # Only PATH and HOME: no API keys or cloud credentials reach the tests.
    env = {"PATH": os.environ["PATH"], "HOME": str(PROJECT)}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=PROJECT, env=env, capture_output=True, text=True,
        timeout=min(120, seconds),  # never past the agent's own deadline
    )
    return (result.stdout + result.stderr)[-6000:]


def execute_tool(name: str, args: dict, seconds: float = 120) -> str:
    if name == "read_file":
        return safe_path(args["path"]).read_text()
    if name == "write_file":
        content = args["content"]
        if len(content) > MAX_FILE_BYTES:
            raise ToolDenied("content is too large")
        safe_path(args["path"], must_exist=False).write_text(content)
        return f"Wrote {len(content)} characters to {args['path']}"
    if name == "run_tests":
        if seconds <= 0:
            raise ToolDenied("no time left to run the tests")
        return run_tests(seconds)
    raise ToolDenied(f"Unknown tool: {name}")
