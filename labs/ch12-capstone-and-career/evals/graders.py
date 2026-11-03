# Generated from src/content/chapters (chapter 12) by `npm run labs`. Edit the chapter, not this file.
def grade_case(case: dict, answer, judge) -> dict[str, bool]:
    """Separate checks for one case; it passes only if all are true."""
    if not case["answerable"]:
        checks = {"abstained": answer.abstained}
    else:
        cited = {c.doc_id for c in answer.citations}
        text = answer.text.lower()
        checks = {
            "answered": not answer.abstained,
            "correct": all(f.lower() in text for f in case["must_include"]),
            # Validity: only cites passages that retrieval returned.
            "sources_valid": cited <= set(answer.retrieved_ids),
            # Coverage: cites at least one passage a human marked relevant.
            "cites_relevant": bool(cited & set(case["relevant_ids"])),
            # Support: every claim is backed by the cited quotes.
            "supported": judge(answer.text,
                               [c.quote for c in answer.citations]),
        }
    # A Verdict object, a string or None would make all() lie:
    # every object is truthy. Only real booleans count.
    not_bool = [k for k, v in checks.items() if not isinstance(v, bool)]
    if not_bool:
        raise TypeError(f"checks must be True or False: {not_bool}")
    return checks
