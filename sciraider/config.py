from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, computed_field
from pydantic_settings import BaseSettings


class GlobalCfg(BaseModel):
    window_days: int = Field(7, ge=1)
    enable_scirate: bool = True
    enable_arxiv: bool = True
    enable_websites: bool = True
    batch_size: int = Field(6, ge=1)

    @computed_field
    @property
    def window(self) -> timedelta:
        return timedelta(days=self.window_days)


class UserCfg(BaseModel):
    id: str
    alias: str
    track_own_papers: bool = False


class SiteCfg(BaseModel):
    name: str
    url: str
    tag: str


class Config(BaseSettings):
    global_: GlobalCfg = Field(alias="global")
    scirate_users: List[UserCfg] = []
    arxiv_authors: List[str] = []
    websites: List[SiteCfg] = []
    cache_dir: Path = Path(".cache")

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }

    def window(self) -> timedelta:
        return self.global_.window
