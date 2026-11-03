"""Shared helpers for the smoke tests.

Each test copies one chapter's generated code into a fresh working directory, adds
the hand-written fixtures it needs, and runs the script as a learner would:
`python script.py` in that directory. PYTHONPATH lists the working directory, then
earlier chapters, nearest first, so `from llm_utils import ...` finds chapter 3.

By default the scripts talk to a local fake Claude server (fake_claude.py), so no
key is needed and nothing leaves the machine. Set LAB_LIVE=1 and ANTHROPIC_API_KEY
to run the same scripts against the real API instead; that costs money, and
assertions that depend on the fake's scripted replies are skipped.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from fake_claude import FakeClaude, default_reply

LABS = Path(__file__).resolve().parents[1]
FIXTURES = LABS / "fixtures"
CHAPTERS = sorted(p for p in LABS.glob("ch[0-9][0-9]-*") if p.is_dir())
LIVE = os.environ.get("LAB_LIVE") == "1"


def chapter_dir(number: int) -> Path:
    return next(p for p in CHAPTERS if p.name.startswith(f"ch{number:02d}-"))


def has(*modules: str) -> bool:
    """True when every module imports: the ML tests need the optional extras."""
    import importlib.util
    return all(importlib.util.find_spec(m) is not None for m in modules)


class Lab:
    def __init__(self, number: int, workdir: Path):
        self.number = number
        self.dir = workdir
        shutil.copytree(chapter_dir(number), workdir, dirs_exist_ok=True)
        self.fake = None

    def add(self, fixture: str, to: str = ".") -> None:
        """Copy labs/fixtures/<fixture> (file or folder) into the working dir."""
        source, target = FIXTURES / fixture, self.dir / to
        if source.is_dir():
            shutil.copytree(source, target / source.name, dirs_exist_ok=True)
        else:
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, target)

    def env(self) -> dict:
        earlier = [str(p) for p in reversed(CHAPTERS[: self.number - 1])]
        env = os.environ | {
            "PYTHONPATH": os.pathsep.join([str(self.dir), *earlier]),
            # As if the venv were activated: scripts that start "python" get this one.
            "PATH": os.pathsep.join([str(Path(sys.executable).parent), os.environ["PATH"]]),
            "PYTHONUNBUFFERED": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "ANONYMIZED_TELEMETRY": "False",  # Chroma
        }
        if not LIVE:
            # A placeholder, never a real key: the fake server ignores it.
            env |= {"ANTHROPIC_API_KEY": "offline-placeholder",
                    "ANTHROPIC_BASE_URL": self.fake.url}
        return env

    def run(self, *args: str, reply=default_reply, stdin: str = "",
            timeout: float = 300, check: bool = True) -> subprocess.CompletedProcess:
        """Run `python <args>` in the working directory, against the fake unless live."""
        with FakeClaude(reply) as fake:
            self.fake = fake
            result = subprocess.run(
                [sys.executable, *args], cwd=self.dir, env=self.env(), input=stdin,
                capture_output=True, text=True, timeout=timeout)
        if check and result.returncode != 0:
            pytest.fail(f"python {' '.join(args)} exited {result.returncode}\n"
                        f"--- stdout\n{result.stdout[-3000:]}\n--- stderr\n{result.stderr[-3000:]}")
        return result


@pytest.fixture
def lab(tmp_path):
    """lab(n) copies chapter n into a temporary working directory."""
    return lambda number: Lab(number, tmp_path / f"ch{number:02d}")


@pytest.fixture(autouse=True)
def _live_needs_key():
    if LIVE and not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("LAB_LIVE=1 needs ANTHROPIC_API_KEY")


offline_only = pytest.mark.skipif(LIVE, reason="checks the fake server's scripted replies")
needs_ml = pytest.mark.skipif(
    not has("sentence_transformers", "chromadb", "transformers"),
    reason="install requirements-ml.txt to run the embedding and RAG labs")
