import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sciraider.email_render import render_digest
from sciraider.scirate_fetch import Paper as SP
from sciraider.arxiv_fetch import Paper as AP
from sciraider.website_watch import SiteChange
from datetime import datetime, timezone


def test_render_digest(tmp_path):
    scite = [SP("Title", "1234.5678", datetime.now(timezone.utc), "user")]
    arxiv = [AP("A Paper", "2345.6789", datetime.now(timezone.utc))]
    sites = [SiteChange("Site", "https://example.com", "tag", datetime.now(timezone.utc))]
    html = render_digest(scite, arxiv, sites, "range")
    assert "Sciraider Digest" in html
