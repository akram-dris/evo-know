import re

class KnowledgeChunkSplitter:
    """Splits documents into semantic chunks suitable for embedding."""

    def __init__(self, chunk_size=512, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        """
        Splits text into chunks of approximately `chunk_size` words/tokens,
        with `chunk_overlap` overlap between consecutive chunks.
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split()
        
        if not words:
            return []
            
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            if i + self.chunk_size >= len(words):
                break
            i += (self.chunk_size - self.chunk_overlap)
            
        return chunks
