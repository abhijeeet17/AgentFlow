import os
from typing import List

class EmbeddingManager:
    def __init__(self):
        self._model = None

    def get_embedding_function(self):
        try:
            from chromadb.utils import embedding_functions
            return embedding_functions.DefaultEmbeddingFunction()
        except Exception:
            return None

    def embed_query(self, text: str) -> List[float]:
        # Return a simple lightweight deterministic float vector for fallback
        import hashlib
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        return [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]

embedding_manager = EmbeddingManager()
