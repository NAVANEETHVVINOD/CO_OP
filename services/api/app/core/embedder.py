import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._lock = asyncio.Lock()

    async def _get_model(self):
        if self.model is None:
            async with self._lock:
                if self.model is None:
                    # Load model in a thread to non-block the event loop fully
                    # but since this is called from embed methods, they already use executors.
                    # Actually, SentenceTransformer download/load is heavy.
                    loop = asyncio.get_running_loop()
                    self.model = await loop.run_in_executor(
                        self.executor,
                        lambda: SentenceTransformer(self.model_name)
                    )
        return self.model

    async def embed_text(self, text: str) -> List[float]:
        model = await self._get_model()
        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(
            self.executor,
            lambda: model.encode(text, normalize_embeddings=True)
        )
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        model = await self._get_model()
        loop = asyncio.get_running_loop()
        embeddings = await loop.run_in_executor(
            self.executor,
            lambda: model.encode(texts, normalize_embeddings=True)
        )
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        return embeddings

# Global singleton instance
embedder = Embedder()
