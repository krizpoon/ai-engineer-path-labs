"""Run one lab script the way the course intends: `python lab.py 7 ingest.py`.

It copies chapter 7's code into labs/work/ch07-rag/ (kept between runs, so the
vector store and manifest survive), adds the chapter's sample data from
labs/fixtures/ when it is missing, and runs the script there with earlier chapters
importable (`from llm_utils import ...` finds chapter 3).

Scripts that call Claude use your ANTHROPIC_API_KEY and cost money; the smoke tests
in labs/smoke/ run the same code against a local fake instead.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parent
CHAPTERS = sorted(p for p in LABS.glob("ch[0-9][0-9]-*") if p.is_dir())
DATA = {".jsonl", ".txt", ".md"}  # results a script may have rewritten: copied only once


def main(argv: list[str]) -> int:
    if len(argv) < 2 or not argv[0].isdigit():
        print(__doc__.strip().splitlines()[0])
        for chapter in CHAPTERS:
            files = sorted(str(p.relative_to(chapter)) for p in chapter.rglob("*")
                           if p.is_file() and "__pycache__" not in p.parts)
            print(f"  {chapter.name[2:4]}  {', '.join(files)}")
        return 2
    number = int(argv[0])
    source = next((p for p in CHAPTERS if p.name.startswith(f"ch{number:02d}-")), None)
    if source is None:
        print(f"No chapter {number} in labs/")
        return 2

    work = LABS / "work" / source.name
    for path in source.rglob("*"):
        if path.is_dir() or "__pycache__" in path.parts:
            continue
        target = work / path.relative_to(source)
        if target.exists() and path.suffix in DATA:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, target)
    fixtures = LABS / "fixtures" / f"ch{number:02d}"
    if fixtures.is_dir():
        for path in fixtures.rglob("*"):
            target = work / path.relative_to(fixtures)
            if path.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(path, target)

    earlier = [str(p) for p in reversed(CHAPTERS[: number - 1])]
    env = os.environ | {"PYTHONPATH": os.pathsep.join([str(work), *earlier])}
    print(f"[lab] chapter {number} in {work.relative_to(LABS.parent)}", file=sys.stderr)
    command = ["bash"] if argv[1].endswith(".sh") else [sys.executable]
    return subprocess.run([*command, *argv[1:]], cwd=work, env=env).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
