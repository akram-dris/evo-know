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
        self._load_if_exists()
        start_id = self.index.ntotal
        self.index.add(embeddings)
        for i, chunk_id in enumerate(chunk_ids):
            self.id_map[start_id + i] = str(chunk_id)
        self.save()

    def search(self, query_embedding: np.ndarray, top_k=5) -> list[dict]:
        """Searches for top-K similar chunks using cosine similarity."""
        self._load_if_exists()
        if self.index.ntotal == 0:
            return []
            
        # Ensure query_embedding is 2D (batch_size, dimension) for FAISS search
        if len(query_embedding.shape) == 1:
            query_embedding = np.expand_dims(query_embedding, axis=0)

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
        index_file = f"{self.index_path}.index"
        map_file = f"{self.index_path}.map"
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, index_file)
        with open(map_file, "wb") as f:
            pickle.dump(self.id_map, f)
        if os.path.exists(index_file):
            self._last_loaded_time = os.path.getmtime(index_file)

    def reset(self):
        """Resets the index and mapping to an empty state."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = {}
        self.save()

    def _load_if_exists(self):
        """Loads existing FAISS index and ID mapping from disk if available."""
        index_file = f"{self.index_path}.index"
        map_file = f"{self.index_path}.map"
        if os.path.exists(index_file) and os.path.exists(map_file):
            mtime = os.path.getmtime(index_file)
            if not hasattr(self, "_last_loaded_time") or mtime > self._last_loaded_time:
                self.index = faiss.read_index(index_file)
                with open(map_file, "rb") as f:
                    self.id_map = pickle.load(f)
                self._last_loaded_time = mtime
