# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
import hashlib
import json
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)
from transformers import AutoTokenizer

from chunker import chunk_text  # the chunker from chapter 6

MODEL = "all-MiniLM-L6-v2"  # reads at most 256 word pieces (chapter 6)
MAX_TOKENS = 200            # room for the special tokens it adds
OVERLAP = 30

ROOT = Path("handbook")
MANIFEST = Path("manifest.json")  # path -> {"hash": ..., "ids": [...]}

tokenizer = AutoTokenizer.from_pretrained(f"sentence-transformers/{MODEL}")
embed = SentenceTransformerEmbeddingFunction(model_name=MODEL)
store = chromadb.PersistentClient(path="./vector-store")
collection = store.get_or_create_collection(
    name="handbook", embedding_function=embed)
manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}


def n_tokens(text: str) -> int:
    return len(tokenizer.tokenize(text))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def save():
    MANIFEST.write_text(json.dumps(manifest, indent=2))


def ingest(root: Path = ROOT) -> None:
    current = {str(p): p.read_text(encoding="utf-8")
               for p in root.glob("**/*.md")}

    # Deleted or renamed files: remove every chunk they had
    for path in sorted(set(manifest) - set(current)):
        collection.delete(ids=manifest.pop(path)["ids"])
        save()

    # New or changed files: replace all of the document's chunks
    for path, text in sorted(current.items()):
        old = manifest.get(path)
        if old and old["hash"] == digest(text):
            continue  # unchanged
        if old:
            collection.delete(ids=old["ids"])
        chunks = (chunk_text(text, MAX_TOKENS, overlap=OVERLAP,
                             length=n_tokens)
                  if text.strip() else [])  # empty file: no chunks
        ids = [f"{path}#{i}" for i in range(len(chunks))]
        # handbook/<group>/... : the first folder names who may read it
        parts = Path(path).relative_to(root).parts
        access = parts[0] if len(parts) > 1 else "everyone"
        if chunks:
            collection.add(
                ids=ids,
                documents=chunks,
                metadatas=[{"source": path, "chunk": i, "access": access}
                           for i in range(len(chunks))],
            )
        manifest[path] = {"hash": digest(text), "ids": ids}
        save()


if __name__ == "__main__":
    ingest()
    print(collection.count(), "chunks indexed")
