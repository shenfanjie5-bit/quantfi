from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


class _MiniDF(list):
    @property
    def empty(self) -> bool:
        return len(self) == 0

    @property
    def columns(self):
        return []

    def sort_values(self, *_args, **_kwargs):
        return self

    def reset_index(self, drop: bool = True):
        return self

    def to_dict(self, orient: str = "records"):
        return list(self)


try:
    import pandas as pd
except Exception:  # pragma: no cover
    class _PD:
        DataFrame = _MiniDF
    pd = _PD()

try:
    import tushare as ts
except Exception:  # pragma: no cover
    ts = None


@dataclass
class APIResult:
    name: str
    ok: bool
    data: Any
    reason: str | None = None


class TuShareClient:
    def __init__(self, token: str):
        self.pro = ts.pro_api(token) if (token and ts is not None) else None

    def call(self, name: str, **kwargs: Any) -> APIResult:
        if self.pro is None:
            return APIResult(name=name, ok=False, data=pd.DataFrame(), reason="missing_tushare_token")
        try:
            func = getattr(self.pro, name)
            df = func(**kwargs)
            if df is None:
                df = pd.DataFrame()
            if not df.empty:
                df = df.sort_values(list(df.columns)).reset_index(drop=True)
            return APIResult(name=name, ok=True, data=df)
        except Exception as exc:
            return APIResult(name=name, ok=False, data=pd.DataFrame(), reason=f"{type(exc).__name__}:{exc}")


def to_raw_records(api: str, df: Any, data_version: str) -> list[dict]:
    out = []
    for row in df.to_dict(orient="records"):
        announce_time = row.get("ann_date") or row.get("f_ann_date") or row.get("pub_time")
        if announce_time:
            announce_time = datetime.fromisoformat(str(announce_time).replace(" ", "T"))
        trade_date = row.get("trade_date")
        out.append(
            {
                "api_name": api,
                "ts_code": row.get("ts_code"),
                "trade_date": trade_date,
                "announce_time": announce_time,
                "payload": row,
                "data_version": data_version,
            }
        )
    return out
