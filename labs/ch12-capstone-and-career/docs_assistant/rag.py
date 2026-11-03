# Generated from src/content/chapters (chapter 12) by `npm run labs`. Edit the chapter, not this file.
from dataclasses import dataclass
from pathlib import Path

import anthropic

from docs_assistant.llm_utils import check_stop, response_text
from docs_assistant.retriever import search

client = anthropic.Anthropic()
PROMPT_VERSION = "answer/v1"
SYSTEM = Path(f"prompts/{PROMPT_VERSION}.txt").read_text()
ABSTAIN = "I don't know. The documents I can see don't answer that."

@dataclass
class Citation:
    doc_id: str
    quote: str

@dataclass
class Answer:
    text: str
    citations: list[Citation]  # evidence: passages the answer cites
    retrieved_ids: list[str]   # diagnostics: what retrieval returned
    abstained: bool

def answer_question(question: str, user) -> Answer:
    # Filter by the user's access before anything reaches the model.
    chunks = search(question, groups=user.groups, k=5)
    retrieved_ids = [c["id"] for c in chunks]
    if not chunks:
        return Answer(ABSTAIN, [], [], abstained=True)

    documents = [
        {
            "type": "document",
            "source": {"type": "text", "media_type": "text/plain",
                       "data": c["text"]},
            "title": c["id"],
            "citations": {"enabled": True},
        }
        for c in chunks
    ]
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=2000,
        system=SYSTEM,  # answer only from the documents, or say you don't know
        messages=[{
            "role": "user",
            "content": [*documents, {"type": "text", "text": question}],
        }],
    )
    check_stop(response)  # truncated or refused: an error, not an answer

    citations = [
        Citation(chunks[cite.document_index]["id"], cite.cited_text)
        for block in response.content
        if block.type == "text"
        for cite in block.citations or []
    ]
    if not citations:  # no evidence: treat it as "I don't know"
        return Answer(ABSTAIN, [], retrieved_ids, abstained=True)
    return Answer(response_text(response), citations, retrieved_ids, False)
