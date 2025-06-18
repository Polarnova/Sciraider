from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List

import aiofiles
import httpx
from selectolax.parser import HTMLParser

from .config import SiteCfg

UA = "SciraiderBot/0.1"


@dataclass
class SiteChange:
    name: str
    tag: str
    ts: datetime


async def diff_sites(sites: Iterable[SiteCfg], window: timedelta, cache_dir: Path, batch_size: int) -> List[SiteChange]:
    results: list[SiteChange] = []
    cache_dir.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(batch_size)

    async def check(site: SiteCfg) -> None:
        async with sem, httpx.AsyncClient(headers={"user-agent": UA}, timeout=10.0) as client:
            retries = 2
            for attempt in range(retries + 1):
                try:
                    resp = await client.get(site.url)
                    resp.raise_for_status()
                    break
                except httpx.HTTPError:
                    if attempt >= retries:
                        return
                    await asyncio.sleep(2 ** attempt)
            parser = HTMLParser(resp.text)
            for tag in parser.css("script,style"):
                tag.decompose()
            text = parser.text(separator=" ", strip=True)
            sha = hashlib.sha256(text.encode()).hexdigest()

        cache_file = cache_dir / f"{site.tag}.sha"
        prev_sha = None
        if cache_file.exists():
            async with aiofiles.open(cache_file, "r") as f:
                prev_sha = (await f.read()).strip()
        if sha != prev_sha:
            now = datetime.now(timezone.utc)
            stat = cache_file.stat().st_mtime if cache_file.exists() else 0
            mod_time = datetime.fromtimestamp(stat, tz=timezone.utc)
            if not cache_file.exists() or mod_time >= datetime.now(timezone.utc) - window:
                results.append(SiteChange(site.name, site.tag, now))
            async with aiofiles.open(cache_file, "w") as f:
                await f.write(sha)

    await asyncio.gather(*(check(s) for s in sites))
    return results
