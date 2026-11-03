# Generated from src/content/chapters (chapter 6) by `npm run labs`. Edit the chapter, not this file.
from chunk_docs import chunk_text, model, n_tokens

filler = ("Staff may book standard-class rail travel "
          "for client visits. ") * 40
paragraph = filler + "Claims above £500 need a director's approval."
print(n_tokens(paragraph))    # far more than 256

whole = model.encode(paragraph, normalize_embeddings=True)
no_rule = model.encode(filler, normalize_embeddings=True)
print(float(whole @ no_rule))    # 1.0: the rule never reached the model

query = model.encode("Who approves large expense claims?",
                     normalize_embeddings=True)
parts = chunk_text(paragraph, max_len=200, length=n_tokens)
vectors = model.encode(parts, normalize_embeddings=True)
print("whole paragraph:", float(whole @ query))
print("best chunk:     ", float((vectors @ query).max()))
