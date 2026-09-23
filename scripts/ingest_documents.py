import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.rag.ingestion import ingest_knowledge_base

if __name__ == "__main__":
    kb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge_base"))
    print(f"Ingesting knowledge base from: {kb_path}")
    chunks = ingest_knowledge_base(kb_path)
    print(f"Successfully ingested {chunks} document chunks into ChromaDB!")
