import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load the model synchronously at startup
        self.model = SentenceTransformer(model_name)
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def embed_text(self, text: str) -> List[float]:
        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(
            self.executor,
            lambda: self.model.encode(text, normalize_embeddings=True)
        )
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(
            self.executor,
            lambda: self.model.encode(texts, normalize_embeddings=True)
        )
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        return embeddings

# Global singleton instance
embedder = Embedder()
