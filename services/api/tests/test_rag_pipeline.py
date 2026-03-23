from app.services.chunker import SemanticChunker
from app.services.bm25_encoder import BM25Encoder

def test_chunker_basic():
    chunker = SemanticChunker(chunk_size=10, overlap=2)
    text = "one two three four five six seven eight nine ten eleven twelve thirteen"
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) == 2
    assert chunks[0] == "one two three four five six seven eight nine ten"
    assert chunks[1] == "nine ten eleven twelve thirteen"

def test_bm25_encoder():
    encoder = BM25Encoder(vocab_size=100)
    text = "hello world hello"
    indices, values = encoder.encode(text)
    
    assert len(indices) <= 2
    assert len(values) == len(indices)
    assert sum(values) == 3.0 # "hello" x 2 + "world" x 1
    
    # Verify sorted
    assert list(indices) == sorted(indices)
