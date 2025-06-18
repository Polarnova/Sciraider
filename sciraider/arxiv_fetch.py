from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, List

import httpx
import feedparser

UA = "SciraiderBot/0.1"
API = "https://export.arxiv.org/api/query"


@dataclass
class Paper:
    title: str
    arxiv_id: str
    ts: datetime


async def fetch_arxiv(authors: Iterable[str], window: timedelta, batch_size: int) -> List[Paper]:
    results: list[Paper] = []
    sem = asyncio.Semaphore(batch_size)

    async def query(author: str) -> None:
        params = {
            "search_query": f'au:"{author}"',
            "sortBy": "lastUpdatedDate",
            "max_results": "10",
        }
        async with sem, httpx.AsyncClient(headers={"user-agent": UA}, timeout=10.0) as client:
            retries = 2
            for attempt in range(retries + 1):
                try:
                    resp = await client.get(API, params=params)
                    resp.raise_for_status()
                    break
                except httpx.HTTPError:
                    if attempt >= retries:
                        return
                    await asyncio.sleep(2 ** attempt)
            feed = feedparser.parse(resp.text)
            for e in feed.entries:
                updated = datetime(*e.updated_parsed[:6], tzinfo=timezone.utc)
                if updated < datetime.now(timezone.utc) - window:
                    continue
                arxiv_id = e.id.split("/")[-1]
                results.append(Paper(e.title, arxiv_id, updated))

    await asyncio.gather(*(query(a) for a in authors))
    return results
