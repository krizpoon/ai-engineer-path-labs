# Hand-written lab adapter, not generated: the capstone reuses chapter 7's search(),
# which returns {"id", "text", "source"} for chunks the user's groups may read.
from answer import search  # noqa: F401  labs/ch07, searches ./vector-store

__all__ = ["search"]
