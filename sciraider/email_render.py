from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from jinja2 import Environment, FileSystemLoader

from .scirate_fetch import Paper as ScitePaper
from .arxiv_fetch import Paper as ArxivPaper
from .website_watch import SiteChange


def render_digest(scite: Iterable[ScitePaper], arxiv: Iterable[ArxivPaper], sites: Iterable[SiteChange], range_txt: str) -> str:
    env = Environment(loader=FileSystemLoader("templates"))
    tmpl = env.get_template("digest.html.j2")
    return tmpl.render(
        scite=list(scite),
        arxiv=list(arxiv),
        sites=list(sites),
        range=range_txt,
        generated=datetime.utcnow(),
    )
