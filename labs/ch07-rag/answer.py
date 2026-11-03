# Generated from src/content/chapters (chapter 7) by `npm run labs`. Edit the chapter, not this file.
import anthropic
import chromadb

from ingest import embed  # the same embedding model as ingestion
from llm_utils import check_stop, response_text  # from chapter 3

client = anthropic.Anthropic()
store = chromadb.PersistentClient(path="./vector-store")
collection = store.get_collection("handbook", embedding_function=embed)

SYSTEM = """You answer questions about the company handbook.
Use only the information in the <documents> provided.
If the documents do not contain the answer, say "I couldn't find
that in the handbook" and suggest who might know. Never guess.
Mention the source file for each fact you use."""


def search(question: str, groups: list[str], k: int = 5) -> list[dict]:
    # The filter runs inside the index: chunks this user may not read
    # are never returned, so they can never reach the prompt.
    hits = collection.query(
        query_texts=[question],
        n_results=k,
        where={"access": {"$in": list(groups)}},  # Chroma needs a list
    )
    return [
        {"id": chunk_id, "text": text, "source": meta["source"]}
        for chunk_id, text, meta in zip(
            hits["ids"][0], hits["documents"][0], hits["metadatas"][0])
    ]


def answer(question: str, groups: list[str]) -> str:
    docs = "\n".join(
        f'<document source="{hit["source"]}">\n{hit["text"]}\n</document>'
        for hit in search(question, groups)
    )
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"<documents>\n{docs}\n</documents>\n\n"
                       f"Question: {question}",
        }],
    )
    # A truncated or refused reply raises instead of passing as an answer
    return response_text(check_stop(response))


if __name__ == "__main__":
    # groups come from your login system, never from the question itself
    print(answer("How many days of parental leave do we get?", ["everyone"]))
