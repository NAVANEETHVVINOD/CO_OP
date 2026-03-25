import zlib
import re
from typing import List, Tuple
from collections import Counter

class BM25Encoder:
    """
    Produces sparse vectors (term frequencies) for Qdrant.
    It uses the feature hashing trick to map tokens to integer indices.
    Qdrant will handle the IDF (Inverse Document Frequency) internally
    if the sparse vectors config uses modifier=Modifier.IDF.
    """
    def __init__(self, vocab_size: int = 2**24):
        self.vocab_size = vocab_size

    def tokenize(self, text: str) -> List[str]:
        # Simple whitespace and punctuation tokenizer
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens

    def encode(self, text: str) -> Tuple[List[int], List[float]]:
        tokens = self.tokenize(text)
        token_counts = Counter(tokens)
        
        indices: List[int] = []
        values: List[float] = []
        
        for token, count in token_counts.items():
            # Use crc32 for stable, fast 32-bit hashing
            idx = zlib.crc32(token.encode('utf-8')) % self.vocab_size
            
            # If multiple tokens hash to the same idx, we just add the counts
            # (Though with 2^24, collisions are rare for typical vocabularies)
            if idx in indices:
                existing_pos = indices.index(idx)
                values[existing_pos] += float(count)
            else:
                indices.append(idx)
                values.append(float(count))
                
        # Qdrant expects indices to be sorted
        if indices:
            indices, values = zip(*sorted(zip(indices, values)))
            
        return list(indices), list(values)

# Global singleton
bm25_encoder = BM25Encoder()
