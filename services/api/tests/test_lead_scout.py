import pytest
from unittest.mock import patch

from app.agent.lead_scout import run_lead_scout
from app.db.models import Lead, Tenant


@pytest.mark.asyncio
@patch("app.agent.lead_scout._score_job")
async def test_run_lead_scout(mock_score_job, db_session, monkeypatch):
    # Set Fake LITELLM_URL to trigger the httpx path
    monkeypatch.setenv("LITELLM_URL", "http://litellm:4000")
    
    # Mock the scoring function to return 95.0 for any job
    mock_score_job.return_value = 95.0
    
    # Also patch the fetch function to return a single test job
    with patch("app.agent.lead_scout._fetch_upwork_jobs") as mock_fetch:
        mock_fetch.return_value = [
            {
                "id": "job_123",
                "title": "Python Developer Needed",
                "description": "Build an AI company",
                "url": "https://test.com",
                "budget": "£500",
                "posted": "2026-03-25"
            }
        ]
        
        # Ensure a tenant exists
        import uuid
        tenant_id = uuid.uuid4()
        tenant = Tenant(id=tenant_id, name="Acme Corp")
        db_session.add(tenant)
        await db_session.commit()
        
        await run_lead_scout()
        
        # Verify lead was added to DB
        from sqlalchemy import select
        result = await db_session.execute(select(Lead))
        leads = result.scalars().all()
        assert len(leads) > 0
        assert leads[0].score == 95.0

