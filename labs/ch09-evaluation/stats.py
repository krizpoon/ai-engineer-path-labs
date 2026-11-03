# Generated from src/content/chapters (chapter 9) by `npm run labs`. Edit the chapter, not this file.
import math

def wilson_interval(passed: int, total: int,
                    z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval. Sensible even at 0% and 100%."""
    if total <= 0:
        raise ValueError("no cases: there is no pass rate to estimate")
    if not 0 <= passed <= total:
        raise ValueError("passed must be between 0 and total")
    p = passed / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    margin = z * math.sqrt(
        p * (1 - p) / total + z**2 / (4 * total**2)) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)

# wilson_interval(20, 20)   -> about (0.84, 1.00), not (1, 1)
# wilson_interval(42, 50)   -> about (0.71, 0.92)
# wilson_interval(336, 400) -> about (0.80, 0.87)


def compare(old: dict[str, bool], new: dict[str, bool]) -> float:
    """old/new map case id -> passed, from runs on the SAME cases.
    Prints what changed and returns a two-sided sign-test p-value."""
    if old.keys() != new.keys():
        raise ValueError("both runs must cover the same case ids")
    fixed = sorted(c for c in old if not old[c] and new[c])
    broken = sorted(c for c in old if old[c] and not new[c])
    print(f"fixed {len(fixed)}: {fixed}")
    print(f"broken {len(broken)}: {broken}")

    changed = len(fixed) + len(broken)  # only these carry evidence
    if changed == 0:
        return 1.0
    # If the change did nothing, each changed case is a coin flip.
    # How likely is a split at least this lopsided by chance?
    k = min(len(fixed), len(broken))
    tail = sum(math.comb(changed, i) for i in range(k + 1))
    return min(1.0, 2 * tail / 2**changed)

# 6 fixed, 0 broken -> p ≈ 0.03: unlikely to be luck
# 6 fixed, 4 broken -> p ≈ 0.75: no evidence either way
