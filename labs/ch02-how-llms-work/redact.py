# Generated from src/content/chapters (chapter 2) by `npm run labs`. Edit the chapter, not this file.
import re

PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "api_key": re.compile(r"sk-ant-[\w-]+"),
    "card": re.compile(r"\b\d(?:[ -]?\d){12,15}\b"),
}


def redact(text: str) -> str:
    """Mask obvious secrets and personal data before text is logged."""
    for name, pattern in PATTERNS.items():
        text = pattern.sub(f"[{name}]", text)
    return text


print(redact("Jane (jane@acme.com) pasted sk-ant-abc123 and card 4111 1111 1111 1111."))
# Jane ([email]) pasted [api_key] and card [card].
