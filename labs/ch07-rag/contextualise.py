# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
import anthropic

from llm_utils import check_stop, response_text

client = anthropic.Anthropic()


def contextualise(document: str, chunk: str) -> str:
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=300,
        output_config={"effort": "low"},
        system=[{
            "type": "text",
            "text": f"<document>\n{document}\n</document>",
            "cache_control": {"type": "ephemeral"},   # reuse across every chunk
        }],
        messages=[{
            "role": "user",
            "content": (
                f"<chunk>\n{chunk}\n</chunk>\n"
                "Write one or two sentences that situate this chunk within the document, "
                "to improve search retrieval. Reply with only those sentences."
            ),
        }],
    )
    context = response_text(check_stop(response))
    return f"{context}\n\n{chunk}"   # embed and index this, not the bare chunk
