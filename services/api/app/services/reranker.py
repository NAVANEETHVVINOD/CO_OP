import asyncio
from typing import List, Tuple, Dict, Any
from sentence_transformers import CrossEncoder
from concurrent.futures import ThreadPoolExecutor

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        # Load the CrossEncoder model
        self.model = CrossEncoder(model_name)
        self.executor = ThreadPoolExecutor(max_workers=2)

    async def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks a list of documents based on a query using the CrossEncoder.
        Documents should be dictionaries containing at least a 'text' field.
        """
        if not documents:
            return []
            
        loop = asyncio.get_running_loop()
        
        # CrossEncoder expects a list of pairs: [[query, doc1], [query, doc2], ...]
        pairs = [[query, doc["text"]] for doc in documents]
        
        # Predict scores in a thread pool
        scores = await loop.run_in_executor(
            self.executor,
            lambda: self.model.predict(pairs)
        )
        
        # Attach scores and sort
        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])
            
        # Sort by rerank score descending
        reranked_docs = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        
        return reranked_docs[:top_k]

# Global singleton
reranker = Reranker()
