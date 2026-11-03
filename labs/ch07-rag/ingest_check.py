# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
import os
import tempfile
from pathlib import Path

os.chdir(tempfile.mkdtemp())  # its own handbook, manifest and store
ROOT = Path("handbook")
(ROOT / "everyone").mkdir(parents=True)
(ROOT / "managers").mkdir()

def write(name: str, text: str) -> None:
    (ROOT / name).write_text(text, encoding="utf-8")

rules = [f"Refund rule {i}. " + "Keep the receipt. " * 30 for i in range(6)]
write("everyone/refunds.md", "\n\n".join(rules + ["OLD: ask finance."]))
write("everyone/travel.md", "Book standard-class rail for client visits.")
write("everyone/empty.md", "")
write("managers/pay.md", "Pay bands are reviewed every April.")

import ingest  # noqa: E402  imported after chdir, so it uses this folder

def indexed() -> list[tuple[str, str]]:
    got = ingest.collection.get(include=["documents", "metadatas"])
    return [(m["source"], text)
            for m, text in zip(got["metadatas"], got["documents"])]

def sources() -> set[str]:
    return {source for source, _ in indexed()}

ingest.ingest(ROOT)
assert any("OLD: ask finance." in t for _, t in indexed())
assert all(ingest.n_tokens(t) <= ingest.MAX_TOKENS for _, t in indexed())
assert "handbook/everyone/empty.md" not in sources()   # empty: no chunks

write("everyone/refunds.md", rules[0])                 # shortened
(ROOT / "everyone/travel.md").rename(ROOT / "everyone/trips.md")
(ROOT / "managers/pay.md").unlink()                    # deleted
ingest.ingest(ROOT)

assert not any("OLD: ask finance." in t for _, t in indexed())
assert len([s for s, _ in indexed() if s.endswith("refunds.md")]) == 1
assert sources() == {"handbook/everyone/refunds.md",
                     "handbook/everyone/trips.md"}
before = ingest.collection.count()
ingest.ingest(ROOT)                                    # nothing changed
assert ingest.collection.count() == before
print("ingestion check passed:", sorted(sources()))
