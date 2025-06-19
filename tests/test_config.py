from pathlib import Path
import sys
from pathlib import Path as P
sys.path.insert(0, str(P(__file__).resolve().parents[1]))

from sciraider.cli import load_cfg


def test_load_cfg(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text("""
    global:
      window_days: 1
    """)
    cfg = load_cfg(cfg_file)
    assert cfg.global_.window_days == 1
