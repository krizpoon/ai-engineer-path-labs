# Generated from src/content/chapters (chapter 6) by `npm run labs`. Edit the chapter, not this file.
from sentence_transformers import SentenceTransformer
from chunker import chunk_text

model = SentenceTransformer("all-MiniLM-L6-v2")

def n_tokens(text: str) -> int:
    return len(model.tokenizer.tokenize(text))

if __name__ == "__main__":
    print(model.max_seq_length)    # 256: the input limit
    document = open("handbook.md", encoding="utf-8").read()

    # Stay below 256 to leave room for the special
    # tokens the model adds to every input.
    chunks = chunk_text(document, max_len=200, overlap=30,
                        length=n_tokens)
    assert all(n_tokens(c) <= 200 for c in chunks)
    print(len(chunks), "chunks")
