from __future__ import annotations

import json
from sqlalchemy import text

from quantfi.core.config import Settings
from quantfi.warehouse.repositories import WarehouseRepo


def build_universe(repo: WarehouseRepo, settings: Settings, trade_date: str) -> list[dict]:
    rows: list[dict] = []
    with repo.db.begin() as conn:
        rs = conn.execute(
            text(
                """
                SELECT DISTINCT payload->>'ts_code' AS ts_code
                FROM raw_tushare
                WHERE api_name='sw_daily' AND trade_date=:d
                """
            ),
            {"d": trade_date},
        ).fetchall()
    if rs:
        for r in rs:
            rows.append({"trade_date": trade_date, "ts_code": r[0], "source": "sw_daily", "reason": "industry_membership"})
    else:
        for c in sorted(settings.static_universe):
            rows.append({"trade_date": trade_date, "ts_code": c, "source": "static_fallback", "reason": "sw_daily_not_available"})
    repo.replace_universe(trade_date, rows)
    return rows
