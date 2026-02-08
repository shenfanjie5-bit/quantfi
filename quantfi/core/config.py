from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import os
from pathlib import Path


@dataclass(frozen=True)
class Versions:
    code_version: str
    config_version: str
    feature_version: str = "feature_v1"
    data_version: str = "tushare_pit_v1"


@dataclass
class Settings:
    tushare_token: str = field(default_factory=lambda: os.getenv("TUSHARE_TOKEN", ""))
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/quantfi"
        )
    )
    static_universe: list[str] = field(
        default_factory=lambda: ["000001.SZ", "600000.SH", "000333.SZ", "600519.SH"]
    )
    decision_threshold_buy: float = 0.2
    decision_threshold_sell: float = -0.2

    @classmethod
    def from_file(cls, path: str | None) -> "Settings":
        if not path:
            return cls()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)

    def config_version(self) -> str:
        payload = json.dumps(
            {
                "static_universe": sorted(self.static_universe),
                "decision_threshold_buy": self.decision_threshold_buy,
                "decision_threshold_sell": self.decision_threshold_sell,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        return sha256(payload.encode("utf-8")).hexdigest()[:16]
