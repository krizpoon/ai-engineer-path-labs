# Hand-written lab adapter, not generated: chapter 7's manifest-based ingestion,
# run from the project root with `python -m docs_assistant.ingest`.
from ingest import collection, ingest  # labs/ch07, indexes ./handbook

if __name__ == "__main__":
    ingest()
    print(collection.count(), "chunks indexed")
