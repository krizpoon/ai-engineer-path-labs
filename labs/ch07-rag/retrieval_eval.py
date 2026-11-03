# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
from typing import Callable

# retrieve(question, groups, k) -> [{"id", "text", "source"}, ...]
Retriever = Callable[[str, list[str], int], list[dict]]

test_set = [
    {"question": "How long do refunds take?", "groups": ["everyone"],
     "evidence": ["Refunds are paid within 5 working days."]},
    {"question": "Can I work from abroad?", "groups": ["everyone"],
     "evidence": ["You can work abroad for up to 30 days a year.",
                  "Tell your manager two weeks before you travel."]},
    {"question": "When are pay bands reviewed?",
     "groups": ["everyone", "managers"],
     "evidence": ["Pay bands are reviewed every April."]},
    # The same question from someone who may not read managers/ files:
    # nothing is findable, and the passage must never come back.
    {"question": "When are pay bands reviewed?", "groups": ["everyone"],
     "evidence": [], "restricted": ["Pay bands are reviewed every April."]},
    {"question": "What is the CEO's favourite film?", "groups": ["everyone"],
     "evidence": []},
    # ... 30-100 real questions from users
]


def hit_rate_at_k(runs):
    """Share of questions where at least one piece of evidence came back."""
    return sum(1 for found, wanted in runs if found) / len(runs)


def recall_at_k(runs):
    """Macro average: the share of each question's evidence that came back."""
    return sum(len(found) / len(wanted) for found, wanted in runs) / len(runs)


def found_evidence(case: dict, retrieve: Retriever,
                   k: int) -> tuple[set[str], set[str]]:
    """(evidence found, restricted text that leaked) for one case."""
    texts = [hit["text"]
             for hit in retrieve(case["question"], case["groups"], k)]
    def found(sentences):
        return {s for s in sentences if any(s in text for text in texts)}
    return found(case["evidence"]), found(case.get("restricted", []))


def score_retrieval(cases: list[dict], retrieve: Retriever,
                    k: int = 5) -> dict:
    runs, leaks = [], []
    for case in cases:
        found, leaked = found_evidence(case, retrieve, k)
        leaks += [(case["groups"], text) for text in leaked]
        if case["evidence"]:
            runs.append((found, set(case["evidence"])))
    if leaks:  # an access bug, not a quality score
        raise AssertionError(f"restricted text retrieved: {leaks}")
    if not runs:
        raise ValueError("no answerable cases to score")
    return {"hit_rate": hit_rate_at_k(runs), "recall": recall_at_k(runs),
            "unanswerable": len(cases) - len(runs)}


if __name__ == "__main__":
    from answer import search
    from rerank import search_and_rerank

    for name, retrieve in [("search", search),
                           ("search + rerank", search_and_rerank)]:
        result = score_retrieval(test_set, retrieve, k=5)
        print(f"{name:16} hit rate@5 {result['hit_rate']:.0%}"
              f"  recall@5 {result['recall']:.0%}")
    print(result["unanswerable"], "unanswerable: score these on abstention")
