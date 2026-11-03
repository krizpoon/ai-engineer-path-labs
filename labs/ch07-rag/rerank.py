# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
from sentence_transformers import CrossEncoder

from answer import search

# A small open-source cross-encoder that runs on a laptop CPU
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def search_and_rerank(question: str, groups: list[str], k: int = 5,
                      first: int = 20) -> list[dict]:
    """Same arguments and result shape as search(), so they swap freely."""
    candidates = search(question, groups, k=first)  # filtered, as before
    if not candidates:
        return []
    scores = reranker.predict([(question, c["text"]) for c in candidates])
    ranked = sorted(zip(scores, candidates),
                    key=lambda pair: pair[0], reverse=True)
    return [candidate for _, candidate in ranked[:k]]
