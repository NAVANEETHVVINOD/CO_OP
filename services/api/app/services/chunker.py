from typing import List

class SemanticChunker:
    """
    Very basic sliding window semantic chunker respecting chunk size and overlap.
    A real production semantic chunker would use token counts (e.g., tiktoken) and sentence boundaries,
    but for Phase 0 we use a character-based or rough word-based sliding window.
    """
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        # Using a simple word-based splitting approach
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            
            # Move the pointer forward by chunk_size - overlap
            i += (self.chunk_size - self.overlap)
            
            # Break if no forward progress would be made
            if self.chunk_size <= self.overlap:
                break
                
        return chunks
