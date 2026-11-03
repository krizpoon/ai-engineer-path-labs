# Generated from src/content/chapters (chapter 6) by `npm run labs`. Edit the chapter, not this file.
# pip install chromadb
import chromadb

client = chromadb.PersistentClient(path="./vector-store")
collection = client.get_or_create_collection(name="help-centre")

# Chroma embeds with a small default model (all-MiniLM-L6-v2, so the
# same 256-word-piece limit applies) unless you pass your own vectors.
collection.add(
    ids=["faq-1", "faq-2", "faq-3"],
    documents=[
        "How to recover access to your account if you forget your login.",
        "Refunds are processed within 5 working days.",
        "Two-factor authentication adds a second step when you sign in.",
    ],
    metadatas=[{"section": "account"}, {"section": "billing"}, {"section": "account"}],
)

results = collection.query(
    query_texts=["I can't remember my password"],
    n_results=2,
    where={"section": "account"},     # metadata filter
)
print(results["documents"][0])
