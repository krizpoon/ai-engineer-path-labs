# Generated from src/content/chapters (chapter 6) by `npm run labs`. Edit the chapter, not this file.
import re
from typing import Callable

SEP = "\n\n"

def _fitting_prefix(word: str, max_len: int, length) -> int:
    """How many leading characters of word fit, measured by length()."""
    lo, hi = 0, len(word)   # binary search; word[:lo] always fits
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if length(word[:mid]) <= max_len:
            lo = mid
        else:
            hi = mid - 1
    return lo

def _hard_split(text: str, max_len: int, length) -> list[str]:
    """Pack words into pieces that fit; cut a word only if it alone is too long."""
    pieces, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if length(candidate) <= max_len:
            current = candidate
            continue
        if current:
            pieces.append(current)
        while length(word) > max_len:   # one "word" longer than a chunk
            cut = _fitting_prefix(word, max_len, length)
            if cut == 0:   # also ends the loop: each pass removes >= 1 char
                raise ValueError(f"{word[0]!r} alone is longer than max_len")
            pieces.append(word[:cut])
            word = word[cut:]
        current = word
    if current:
        pieces.append(current)
    return pieces

def _units(text: str, max_len: int, length) -> list[str]:
    """Paragraphs that fit; otherwise sentences; otherwise word groups."""
    units = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        if length(para) <= max_len:
            units.append(para)
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            if length(sentence) <= max_len:
                units.append(sentence)
            else:
                units.extend(_hard_split(sentence, max_len, length))
    return units

def chunk_text(
    text: str,
    max_len: int,
    overlap: int = 0,
    length: Callable[[str], int] = len,
) -> list[str]:
    """Split text into chunks no longer than max_len, measured by length().

    overlap carries whole trailing sentences or paragraphs, up to that
    length, into the next chunk. Use the embedding model's tokenizer as
    length() so chunks fit its input limit.
    """
    if max_len <= 0:
        raise ValueError("max_len must be positive")
    if not 0 <= overlap < max_len:
        raise ValueError("overlap must be >= 0 and < max_len")

    chunks, current = [], []
    for unit in _units(text, max_len, length):
        if current and length(SEP.join(current + [unit])) > max_len:
            chunks.append(SEP.join(current))
            # Carry the tail of the last chunk, if it fits within overlap.
            tail = []
            for part in reversed(current):
                if length(SEP.join([part] + tail)) > overlap:
                    break
                tail.insert(0, part)
            current = tail
            # Drop carried context that no longer leaves room for unit.
            while current and length(SEP.join(current + [unit])) > max_len:
                current.pop(0)
        current.append(unit)
    if current:
        chunks.append(SEP.join(current))
    # The guarantee callers rely on, checked rather than assumed.
    if any(length(c) > max_len for c in chunks):
        raise ValueError("a chunk exceeds max_len; check length()")
    return chunks
