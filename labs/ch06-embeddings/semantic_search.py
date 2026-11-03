# Generated from src/content/chapters (chapter 6) by `npm run labs`. Edit the chapter, not this file.
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")   # 384-dimensional vectors

docs = [
    "How to recover access to your account if you forget your login.",
    "Our office is closed on public holidays.",
    "Refunds are processed within 5 working days.",
    "Two-factor authentication adds a second step when you sign in.",
]

# normalize_embeddings=True makes cosine similarity a plain dot product
doc_vectors = model.encode(docs, normalize_embeddings=True)

query = "I can't remember my password"
query_vector = model.encode(query, normalize_embeddings=True)

scores = doc_vectors @ query_vector          # one similarity per document
for i in np.argsort(-scores):                # highest first
    print(f"{scores[i]:.2f}  {docs[i]}")
