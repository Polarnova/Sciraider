from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from rich.logging import RichHandler
from rich.traceback import install

from .config import Config
import yaml
from .scirate_fetch import fetch_scirate
from .arxiv_fetch import fetch_arxiv
from .website_watch import diff_sites
from .email_render import render_digest

install()
logging.basicConfig(level="INFO", handlers=[RichHandler()])
logger = logging.getLogger(__name__)


async def main(cfg: Config) -> bool:
    window = cfg.window()
    batch_size = cfg.global_.batch_size

    scite = await fetch_scirate(cfg.scirate_users, window, batch_size) if cfg.global_.enable_scirate else []
    arxiv = await fetch_arxiv(cfg.arxiv_authors, window, batch_size) if cfg.global_.enable_arxiv else []
    sites = await diff_sites(cfg.websites, window, cfg.cache_dir, batch_size) if cfg.global_.enable_websites else []

    if not any((scite, arxiv, sites)):
        logger.info("No updates found; skipping email.")
        return False

    range_txt = f"{(datetime.utcnow() - window).date()} to {datetime.utcnow().date()}"
    html = render_digest(scite, arxiv, sites, range_txt)
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "digest.html").write_text(html, encoding="utf-8")
    logger.info("Digest written to %s", out_dir / "digest.html")
    print(f"::set-output name=sent::true")
    print(f"::set-output name=range::{range_txt}")
    return True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--cfg", type=Path, required=True)
    return p.parse_args()


def load_cfg(path: Path) -> Config:
    data = yaml.safe_load(path.read_text())
    return Config.model_validate(data)


if __name__ == "__main__":
    args = parse_args()
    cfg = load_cfg(args.cfg)
    asyncio.run(main(cfg))
