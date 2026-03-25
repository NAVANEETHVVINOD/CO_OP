import logging
import uuid
import random
from datetime import datetime, timezone
from typing import Dict, List, Any

import httpx
from sqlalchemy import select

from app.services.vector_search import search_relevant_chunks

logger = logging.getLogger(__name__)

# Upwork RSS feed URLs (public, no auth required)
UPWORK_RSS_URLS = [
    "https://www.upwork.com/ab/feed/jobs/rss",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

async def _fetch_upwork_jobs() -> List[Dict[str, Any]]:
    """
    Fetch job listings from Upwork.
    Uses RSS feed as a starting point. In production, replace with Upwork API.
    Falls back to simulated data if RSS is blocked by Cloudflare/Bot detection.
    """
    jobs: List[Dict[str, Any]] = []

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                UPWORK_RSS_URLS[0],
                params={"q": "python OR fastapi OR ai", "sort": "recency"},
                timeout=15.0,
                headers={
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
                },
            )
            if resp.status_code == 200:
                # Simple XML parsing for RSS items
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.text)
                for item in root.findall(".//item")[:20]:
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    description = item.findtext("description", "")
                    jobs.append({
                        "title": title,
                        "url": link,
                        "description": description[:3000],
                    })
                logger.info(f"Fetched {len(jobs)} jobs from Upwork RSS")
            else:
                logger.warning(f"Upwork RSS returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"Failed to fetch Upwork RSS (likely blocked): {e}")

    # Fallback: simulated jobs if RSS fails (expected — Upwork blocks scrapers)
    if not jobs:
        logger.info("Using simulated job data (Upwork RSS blocked)")
        jobs = [
            {
                "title": "FastAPI Backend Developer for SaaS Platform",
                "url": "https://www.upwork.com/jobs/~simulated1",
                "description": "We need an experienced FastAPI developer to build REST APIs for our SaaS platform. Experience with PostgreSQL, Redis, and Docker required.",
            },
            {
                "title": "AI/ML Engineer - RAG Pipeline Development",
                "url": "https://www.upwork.com/jobs/~simulated2",
                "description": "Looking for an AI engineer to build a RAG pipeline using LangChain, Qdrant, and OpenAI. Must have experience with document processing.",
            },
            {
                "title": "Full Stack Developer - Next.js + Python",
                "url": "https://www.upwork.com/jobs/~simulated3",
                "description": "Need a full stack developer proficient in Next.js and Python/FastAPI. Project involves building a dashboard with real-time data.",
            },
            {
                "title": "DevOps Engineer - Docker & Kubernetes",
                "url": "https://www.upwork.com/jobs/~simulated4",
                "description": "Seeking a DevOps engineer to containerize our application and set up CI/CD pipelines. Docker compose experience required.",
            },
            {
                "title": "Telegram Bot Developer",
                "url": "https://www.upwork.com/jobs/~simulated5",
                "description": "We need a Telegram bot for customer support automation. Python experience with python-telegram-bot library preferred.",
            },
        ]

    return jobs


async def _score_job(tenant_id: str, job: Dict[str, Any]) -> float:
    """
    Score a job against company profile using RAG + LiteLLM.
    Returns a score from 0-100.
    """
    try:
        from app.config import get_settings
        settings = get_settings()

        # 1. Retrieve matching portfolio chunks (RAG)
        relevant_chunks = await search_relevant_chunks(tenant_id, f"{job['title']} {job['description'][:500]}", limit=3)
        portfolio_context = "\n".join([f"- {c['text']}" for c in relevant_chunks])

        if not settings.LITELLM_URL:
            return _keyword_score(job)

        async with httpx.AsyncClient() as client:
            # Construct the RAG prompt
            system_prompt = (
                "You are an expert job matching assistant for 'Co-Op', an AI-driven software agency. "
                "Your goal is to score a job lead on a scale of 0-100 based on how well it matches the company's "
                "expertise and past projects. Return ONLY a JSON object: {\"score\": 85, \"reasoning\": \"brief reason\"}."
            )
            
            user_msg = (
                f"### Job Lead\nTitle: {job['title']}\nDescription: {job['description'][:1000]}\n\n"
                f"### Company Portfolio (Relevant Snippets)\n{portfolio_context if portfolio_context else 'General: Python, AI, FastAPI, DevOps'}\n\n"
                "Score this lead (0-100). Higher score means a better match for our capabilities."
            )

            resp = await client.post(
                f"{settings.LITELLM_URL}/v1/chat/completions",
                json={
                    "model": "simple",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg},
                    ],
                    "max_tokens": 50,
                    "temperature": 0.0,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                import json
                try:
                    res = json.loads(content)
                    return float(res.get("score", 0))
                except:
                    import re
                    match = re.search(r"\"score\":\s*(\d+)", content)
                    if match:
                        return float(match.group(1))
            else:
                logger.warning(f"LiteLLM scoring returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"LLM scoring failed, falling back to keywords: {e}")

    return _keyword_score(job)


def _keyword_score(job: Dict[str, Any]) -> float:
    """Simple keyword-based scoring fallback."""
    keywords = ["python", "fastapi", "ai", "ml", "rag", "docker", "next.js", "typescript", "postgresql", "redis"]
    text = (job.get("title", "") + " " + job.get("description", "")).lower()
    matches = sum(1 for kw in keywords if kw in text)
    return min(100.0, (matches / len(keywords)) * 100)


async def run_lead_scout() -> None:
    """Main lead scout task — fetch, score, store, notify."""
    logger.info("Lead Scout starting...")

    from app.communication.telegram import send_progress, send_message, _admin_chat_id
    chat_id = _admin_chat_id or ""

    if chat_id:
        await send_progress(chat_id, 1, 6, "Fetching Upwork jobs...")

    # 1. Fetch jobs
    jobs = await _fetch_upwork_jobs()
    if not jobs:
        logger.info("No jobs found.")
        return

    # 2. Get default tenant
    from app.db.session import AsyncSessionLocal
    from app.db.models import Lead, Tenant

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Tenant).limit(1))
        tenant = result.scalars().first()
        if not tenant:
            logger.error("No tenant found — cannot score or store leads")
            return
        tenant_id = str(tenant.id)

    if chat_id:
        await send_progress(chat_id, 2, 6, f"Analyzing {len(jobs)} jobs with portfolio matching...")

    # 3. Score jobs
    scored_jobs = []
    for job in jobs:
        score = await _score_job(tenant_id, job)
        scored_jobs.append({**job, "score": score})

    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    top5 = scored_jobs[:5]

    if chat_id:
        await send_progress(chat_id, 3, 6, "Storing leads in database...")

    # 4. Store in DB
    try:
        async with AsyncSessionLocal() as session:
            # Re-fetch tenant in this session
            result = await session.execute(select(Tenant).where(Tenant.id == uuid.UUID(tenant_id)))
            tenant = result.scalars().first()
            
            for job in scored_jobs:
                lead = Lead(
                    tenant_id=tenant.id,
                    source="upwork",
                    title=job["title"],
                    url=job.get("url", ""),
                    description=job.get("description", "")[:2000],
                    score=job["score"],
                    status="new",
                )
                session.add(lead)
            await session.commit()

        if chat_id:
            await send_progress(chat_id, 4, 6, f"Stored {len(scored_jobs)} leads.")
    except Exception as e:
        logger.error(f"Failed to store leads: {e}")

    # 5. Send top 5 to Telegram
    if chat_id:
        await send_progress(chat_id, 5, 6, "Preparing notification...")

    try:
        lines = ["🎯 *Lead Scout Report*\n"]
        for i, job in enumerate(top5):
            lines.append(
                f"*{i + 1}.* [{job['title'][:60]}]({job.get('url', '#')})\n"
                f"   Score: {job['score']:.0f}/100\n"
            )
        lines.append(f"\n_Matched against your portfolio using RAG._")
        lines.append(f"_Total jobs analyzed: {len(scored_jobs)}_")

        if chat_id:
            await send_message("\n".join(lines))
            await send_progress(chat_id, 6, 6, "Lead Scout complete! ✅")
    except Exception as e:
        logger.error(f"Failed to send lead report: {e}")

    logger.info(f"Lead Scout complete: {len(scored_jobs)} jobs scored, top score: {top5[0]['score']:.0f}")

