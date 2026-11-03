# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
from answer import client, search
from llm_utils import check_stop  # from chapter 3


def answer_with_citations(question: str, groups: list[str]):
    hits = search(question, groups)
    documents = [
        {
            "type": "document",
            "source": {"type": "text", "media_type": "text/plain", "data": hit["text"]},
            "title": hit["source"],
            "citations": {"enabled": True},
        }
        for hit in hits
    ]
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": [*documents, {"type": "text", "text": question}],
        }],
    )
    check_stop(response)
    for block in response.content:
        if block.type != "text":
            continue
        print(block.text, end="")
        for cite in block.citations or []:
            quote = cite.cited_text[:60]
            print(f' [{cite.document_title}: "{quote}..."]', end="")
    print()


if __name__ == "__main__":
    answer_with_citations("How long do refunds take?", ["everyone"])
