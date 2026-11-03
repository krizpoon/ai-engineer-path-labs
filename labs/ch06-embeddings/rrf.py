# Generated from src/content/chapters (chapter 6) by `npm run labs`. Edit the chapter, not this file.
def reciprocal_rank_fusion(*ranked_lists: list[str], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranking in ranked_lists:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)

keyword_hits = ["faq-7", "faq-2", "faq-9"]    # from BM25, e.g. the rank_bm25 package
semantic_hits = ["faq-2", "faq-4", "faq-7"]   # from your vector search

print(reciprocal_rank_fusion(keyword_hits, semantic_hits))
# ['faq-2', 'faq-7', 'faq-4', 'faq-9']
