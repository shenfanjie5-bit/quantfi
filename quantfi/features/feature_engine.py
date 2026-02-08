from __future__ import annotations

from collections import defaultdict
from datetime import datetime


def build_features(repo: WarehouseRepo, trade_date: str, feature_version: str) -> list[dict]:
    bars = repo.load_recent_bars(trade_date, lookback=30)
    by_code = defaultdict(list)
    for b in bars:
        by_code[b["ts_code"]].append(b)
    rows = []
    universe = repo.load_universe(trade_date)
    for code in universe:
        hist = sorted([x for x in by_code.get(code, []) if str(x["trade_date"]) <= trade_date], key=lambda x: str(x["trade_date"]))
        if len(hist) < 2:
            continue
        close = [h.get("close_adj") or h.get("close") or 0.0 for h in hist]
        ret1 = (close[-1] / close[-2] - 1.0) if close[-2] else 0.0
        ma5 = sum(close[-5:]) / min(5, len(close))
        trend = (close[-1] / ma5 - 1.0) if ma5 else 0.0
        suspended = bool(hist[-1].get("is_suspended"))
        limit_up = bool(hist[-1].get("is_limit_up"))
        limit_down = bool(hist[-1].get("is_limit_down"))
        rows.append(
            {
                "trade_date": trade_date,
                "ts_code": code,
                "feature_version": feature_version,
                "payload": {
                    "ret_1d": ret1,
                    "trend_ma5": trend,
                    "is_suspended": suspended,
                    "is_limit_up": limit_up,
                    "is_limit_down": limit_down,
                    "as_of_trade_date": trade_date,
                },
                "as_of_time": datetime.fromisoformat(f"{trade_date}T15:00:00"),
            }
        )
    repo.upsert_features(rows)
    return rows
