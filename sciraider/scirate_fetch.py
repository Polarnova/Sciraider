from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, List

import httpx
from selectolax.parser import HTMLParser

from .config import UserCfg

UA = "SciraiderBot/0.1"
DATE_RE = re.compile(r"[A-Z][a-z]{2} \d{1,2} \d{4}")


@dataclass
class Paper:
    title: str
    arxiv_id: str
    ts: datetime
    user: str


async def fetch_scirate(
    users: Iterable[UserCfg], window: timedelta, batch_size: int
) -> List[Paper]:
    results: list[Paper] = []
    sem = asyncio.Semaphore(batch_size)

    async def fetch_one(user: UserCfg) -> None:
        url = f"https://scirate.com/{user.id}"
        async with sem, httpx.AsyncClient(headers={"user-agent": UA}, follow_redirects=True, timeout=10.0) as client:
            retries = 2
            for attempt in range(retries + 1):
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    break
                except httpx.HTTPError:
                    if attempt >= retries:
                        return
                    await asyncio.sleep(2 ** attempt)
            parser = HTMLParser(resp.text)
            for a in parser.css("a[href^='/paper/']"):
                date_node = a.parent.previous
                if not date_node:
                    continue
                m = DATE_RE.search(date_node.text())
                if not m:
                    continue
                ts = datetime.strptime(m.group(), "%b %d %Y").replace(tzinfo=timezone.utc)
                if ts < datetime.now(timezone.utc) - window:
                    continue
                arxiv_id = a.attributes.get("href", "").split("/")[-1]
                title = a.text(strip=True)
                results.append(Paper(title, arxiv_id, ts, user.alias))

    await asyncio.gather(*(fetch_one(u) for u in users))
    return results
