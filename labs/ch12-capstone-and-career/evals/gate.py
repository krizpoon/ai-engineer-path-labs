# Generated from src/content/chapters (chapter 12) by `npm run labs`. Edit the chapter, not this file.
"""Pure comparison logic for the CI gate, so it can be unit-tested."""
import hashlib
import json

# Starter value. Run main several times, count how many cases flip
# by chance, and set this just above that.
MAX_NET_REGRESSIONS = 2

def case_hash(case: dict) -> str:
    """Changes whenever a case's question, facts or flags change."""
    text = json.dumps(case, sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def check_suite(cases: list[dict]) -> None:
    if not cases:
        raise ValueError("no eval cases: an empty suite cannot pass")
    ids = [c["id"] for c in cases]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"duplicate case ids: {dupes}")

def gate(baseline: dict, current: dict, retired: set[str]) -> list[str]:
    """Each run is {"dataset_version": str, "cases": {id: result}}, where
    a result has "passed", "critical" and "hash". Returns the reasons to
    fail; an empty list means the gate passes."""
    old, new = baseline["cases"], current["cases"]
    if not new:
        return ["no cases ran"]
    failures = []

    # Removed cases: only deliberate, listed, non-critical removals.
    missing = sorted(set(old) - set(new) - retired)
    if missing:
        failures.append(f"baseline cases missing from this run: {missing}")
    retired_critical = sorted(i for i in retired & set(old)
                              if old[i]["critical"])
    if retired_critical:
        failures.append(f"critical cases cannot be retired: {retired_critical}")

    # Critical on main stays critical, even if the flag was dropped.
    critical = {i for i, r in new.items() if r["critical"]}
    critical |= {i for i, r in old.items() if r["critical"] and i in new}
    failed = sorted(i for i in critical if not new[i]["passed"])
    if failed:
        failures.append(f"critical cases failed: {failed}")

    # Compare only cases that are unchanged since the baseline.
    same = [i for i in new if i in old and old[i]["hash"] == new[i]["hash"]]
    broke = [i for i in same if old[i]["passed"] and not new[i]["passed"]]
    fixed = [i for i in same if not old[i]["passed"] and new[i]["passed"]]
    if len(broke) - len(fixed) > MAX_NET_REGRESSIONS:
        failures.append(f"net regressions over the allowance: broke "
                        f"{broke}, fixed {fixed}")

    if baseline["dataset_version"] != current["dataset_version"]:
        added = sorted(set(new) - set(old))
        edited = sorted(i for i in new if i in old and i not in same)
        print(f"Suite changed: added {added}, edited {edited}, "
              f"retired {sorted(retired & set(old))}")
    return failures
