import os
import faiss
import numpy as np
import pickle

class VectorStore:
    """FAISS vector database wrapper for semantic search and similarity matching."""
    
    def __init__(self, dimension=384, index_path="/data/faiss_index"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine on normalized)
        self.id_map = {}  # faiss_id → chunk_uuid
        self._load_if_exists()

    def add(self, embeddings: np.ndarray, chunk_ids: list[str]):
        """Adds normalized embeddings and their associated chunk UUIDs to the FAISS index."""
        start_id = self.index.ntotal
        self.index.add(embeddings)
        for i, chunk_id in enumerate(chunk_ids):
            self.id_map[start_id + i] = str(chunk_id)
        self.save()

    def search(self, query_embedding: np.ndarray, top_k=5) -> list[dict]:
        """Searches for top-K similar chunks using cosine similarity."""
        if self.index.ntotal == 0:
            return []
            
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.id_map:
                results.append({
                    "id": self.id_map[idx],
                    "score": float(distances[0][i])
                })
        return results

    def save(self):
        """Persists the FAISS index and ID mapping to disk."""
        os.makedirs(os.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, f"{self.index_path}.index")
        with open(f"{self.index_path}.map", "wb") as f:
            pickle.dump(self.id_map, f)

    def _load_if_exists(self):
        """Loads existing FAISS index and ID mapping from disk if available."""
        if os.path.exists(f"{self.index_path}.index") and os.path.exists(f"{self.index_path}.map"):
            self.index = faiss.read_index(f"{self.index_path}.index")
            with open(f"{self.index_path}.map", "rb") as f:
                self.id_map = pickle.load(f)
