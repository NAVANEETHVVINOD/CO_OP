import pytest
from unittest.mock import patch, MagicMock

from app.agent.lead_scout import _fetch_upwork_jobs, _keyword_score, run_lead_scout
from app.db.models import Lead

@pytest.mark.asyncio
async def test_score_job_local():
    # Test keyword fallback scoring
    job_description = "We need an AI agent builder using Python and FastAPI."
    score = _keyword_score({"title": "AI agent", "description": job_description})
    assert score > 0

@pytest.mark.asyncio
async def test_run_lead_scout(db_session):
    with patch("app.agent.lead_scout._fetch_upwork_jobs") as mock_fetch, \
         patch("app.agent.lead_scout._score_job") as mock_score, \
         patch("app.agent.lead_scout.send_message") as mock_send_message, \
         patch("app.agent.lead_scout.send_progress") as mock_send_progress, \
         patch("app.agent.lead_scout.AsyncSessionLocal") as mock_session_local:
         
        mock_session_local.return_value.__aenter__.return_value = db_session
        
        # Mock fetched jobs
        mock_fetch.return_value = [
            {"title": "AI Dev", "description": "Need an expert", "url": "http://test.com/1", "source": "upwork"}
        ]
        
        # Mock scoring
        mock_score.return_value = 8.0
        
        await run_lead_scout(db_session)
        
        # Verify lead was added to DB
        from sqlalchemy import select
        result = await db_session.execute(select(Lead))
        leads = result.scalars().all()
        assert len(leads) > 0
        assert leads[0].title == "AI Dev"
        assert leads[0].score == 8
