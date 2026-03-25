import pytest
import uuid
from app.services.search import _compute_rrf, hybrid_search
from qdrant_client.models import ScoredPoint

def test_compute_rrf_simple():
    # Setup mock scored points
    hit1 = ScoredPoint(id=1, version=1, score=0.9, payload={"text": "doc1"})
    hit2 = ScoredPoint(id=2, version=1, score=0.8, payload={"text": "doc2"})
    
    dense = [hit1, hit2]
    sparse = [hit2, hit1]
    
    # RRF with alpha=0.5 should give equal weight
    results = _compute_rrf(dense, sparse, alpha=0.5, k=60)
    
    assert len(results) == 2
    # Score for doc1: 0.5 * (1/(60+1)) + 0.5 * (1/(60+2))
    # Score for doc2: 0.5 * (1/(60+1)) + 0.5 * (1/(60+2))
    # They should be equal
    assert results[0]["rrf_score"] == results[1]["rrf_score"]

def test_compute_rrf_weighted():
    hit1 = ScoredPoint(id=1, version=1, score=0.9, payload={"text": "doc1"})
    hit2 = ScoredPoint(id=2, version=1, score=0.8, payload={"text": "doc2"})
    
    dense = [hit1]
    sparse = [hit2]
    
    # alpha=1.0 means only dense results matter
    results = _compute_rrf(dense, sparse, alpha=1.0, k=60)
    assert results[0]["text"] == "doc1"
    
    # alpha=0.0 means only sparse results matter
    results = _compute_rrf(dense, sparse, alpha=0.0, k=60)
    assert results[0]["text"] == "doc2"

@pytest.mark.asyncio
async def test_hybrid_search_flow(mocker):
    # Mock dependencies
    mock_embed = mocker.patch("app.services.search.embedder.embed_text")
    mock_embed.return_value = [0.1] * 384
    
    mock_bm25 = mocker.patch("app.services.search.bm25_encoder.encode")
    mock_bm25.return_value = ([1, 2], [0.5, 0.5])
    
    mock_qdrant = mocker.patch("app.db.qdrant_client.qdrant.query_points", new_callable=mocker.AsyncMock)
    hit = ScoredPoint(id=str(uuid.uuid4()), version=1, score=0.9, payload={"text": "found content"})
    mock_qdrant.return_value = mocker.MagicMock(points=[hit])
    
    mock_rerank = mocker.patch("app.services.search.reranker.rerank")
    mock_rerank.return_value = [{"text": "found content", "rerank_score": 0.95}]
    
    tenant_id = uuid.uuid4()
    results = await hybrid_search("test query", tenant_id, top_k=1)
    
    assert len(results) == 1
    assert results[0]["text"] == "found content"
    mock_embed.assert_called_once()
    mock_bm25.assert_called_once()
    assert mock_qdrant.call_count == 2 # One for dense, one for sparse
    mock_rerank.assert_called_once()
