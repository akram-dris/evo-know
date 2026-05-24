from sentence_transformers import SentenceTransformer
import numpy as np

class KnowledgeEncoder:
    """Wrapper for Sentence-Transformers multilingual embedding model."""
    
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encodes a list of text strings into normalized numpy embeddings."""
        return self.model.encode(texts, normalize_embeddings=True)
