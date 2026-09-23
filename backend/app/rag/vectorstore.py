import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.rag.embeddings import embedding_manager

class VectorStoreManager:
    def __init__(self):
        self.chroma_dir = os.path.abspath(settings.CHROMADB_DIR)
        os.makedirs(self.chroma_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.chroma_dir)
        self.collection_name = settings.CHROMADB_COLLECTION
        self.ef = embedding_manager.get_embedding_function()
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        if not documents:
            return
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 3) -> dict:
        count = self.collection.count()
        if count == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        actual_n = min(n_results, count)
        results = self.collection.query(
            query_texts=[query_text],
            n_results=actual_n
        )
        return results

    def reset_collection(self):
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )

vector_store_manager = VectorStoreManager()
