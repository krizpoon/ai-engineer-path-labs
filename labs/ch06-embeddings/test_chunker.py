# Generated from src/content/chapters (chapter 6) by `npm run labs`. Edit the chapter, not this file.
import pytest
from chunker import chunk_text

def utf8_bytes(text: str) -> int:
    return len(text.encode("utf-8"))

def test_long_paragraph_is_split():
    paragraph = "One short sentence here. " * 50
    chunks = chunk_text(paragraph, max_len=100)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)

def test_zero_overlap_repeats_nothing():
    text = "\n\n".join(f"Paragraph {i} " + "x" * 40 for i in range(6))
    chunks = chunk_text(text, max_len=120, overlap=0)
    assert "".join(chunks).count("Paragraph 0") == 1

def test_custom_length_holds_for_multibyte_text():
    # "é" is 2 bytes; cutting 5 characters would give 10-byte pieces.
    chunks = chunk_text("é" * 10, max_len=5, length=utf8_bytes)
    assert all(utf8_bytes(c) <= 5 for c in chunks)
    assert "".join(chunks) == "é" * 10

def test_unsplittable_character_is_rejected():
    with pytest.raises(ValueError):
        chunk_text("€", max_len=2, length=utf8_bytes)   # 3 bytes
