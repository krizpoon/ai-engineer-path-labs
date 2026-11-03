# Generated from src/content/chapters (chapter 12) by `npm run labs`. Edit the chapter, not this file.
"""Test users for evals: one per set of groups a case asks as."""
from dataclasses import dataclass

@dataclass(frozen=True)
class EvalUser:
    name: str
    groups: tuple[str, ...]

def user_for(groups: list[str]) -> EvalUser:
    return EvalUser("eval-" + ("-".join(sorted(groups)) or "none"),
                    tuple(groups))
