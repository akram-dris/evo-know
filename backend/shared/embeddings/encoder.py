from sentence_transformers import SentenceTransformer
import numpy as np

class KnowledgeEncoder:
    """Wrapper for Sentence-Transformers multilingual embedding model."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KnowledgeEncoder, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        if getattr(self, '_initialized', False):
            return
        self.model = SentenceTransformer(model_name)
        self._initialized = True

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encodes a list of text strings into normalized numpy embeddings."""
        return self.model.encode(texts, normalize_embeddings=True)
