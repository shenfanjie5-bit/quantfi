from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from quantfi.core.tushare_client import TuShareClient, to_raw_records
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quantfi.warehouse.repositories import WarehouseRepo


MVP_APIS = ["stock_basic", "trade_cal", "daily", "adj_factor", "suspend_d", "limit_list_d", "index_daily", "sw_daily", "daily_basic"]


@dataclass
class IngestState:
    degrade_reasons: list[str] = field(default_factory=list)
    confidence_penalty: float = 0.0

    def degrade(self, reason: str, penalty: float = 0.08) -> None:
        self.degrade_reasons.append(reason)
        self.confidence_penalty += penalty


def ingest_daily(client: TuShareClient, repo: WarehouseRepo, trade_date: str, data_version: str) -> IngestState:
    state = IngestState()
    raw_records: list[dict] = []

    params = {
        "stock_basic": {"exchange": "", "list_status": "L", "fields": "ts_code,symbol,name,industry,list_date"},
        "trade_cal": {"exchange": "SSE", "start_date": trade_date, "end_date": trade_date},
        "daily": {"trade_date": trade_date},
        "adj_factor": {"trade_date": trade_date},
        "suspend_d": {"trade_date": trade_date},
        "limit_list_d": {"trade_date": trade_date},
        "index_daily": {"trade_date": trade_date},
        "sw_daily": {"trade_date": trade_date},
        "daily_basic": {"trade_date": trade_date},
    }

    results: dict[str, Any] = {}
    for api in MVP_APIS:
        res = client.call(api, **params[api])
        if not res.ok:
            state.degrade(f"{api}_unavailable:{res.reason}")
            results[api] = []
            continue
        results[api] = res.data
        raw_records.extend(to_raw_records(api, res.data, data_version))

    raw_records = dedup_raw_records(raw_records)
    repo.insert_raw_records(raw_records)
    _upsert_ods(results, repo, trade_date, state)
    return state


def _upsert_ods(results: dict[str, Any], repo: WarehouseRepo, trade_date: str, state: IngestState) -> None:
    daily = results.get("daily", [])
    if getattr(daily, "empty", True):
        state.degrade("daily_empty")
        return
    adj = results.get("adj_factor", [])
    sus = results.get("suspend_d", [])
    lim = results.get("limit_list_d", [])

    adj_map = {r["ts_code"]: float(r.get("adj_factor", 1.0)) for r in adj.to_dict("records")} if not getattr(adj, "empty", True) else {}
    sus_set = {r.get("ts_code") for r in sus.to_dict("records")} if not getattr(sus, "empty", True) else set()
    lim_map = {r.get("ts_code"): r.get("limit") for r in lim.to_dict("records")} if not getattr(lim, "empty", True) else {}

    rows = []
    for r in daily.to_dict("records"):
        ts_code = r["ts_code"]
        af = adj_map.get(ts_code, 1.0)
        limit_flag = lim_map.get(ts_code)
        rows.append(
            {
                "ts_code": ts_code,
                "trade_date": trade_date,
                "open": r.get("open"),
                "high": r.get("high"),
                "low": r.get("low"),
                "close": r.get("close"),
                "vol": r.get("vol"),
                "amount": r.get("amount"),
                "adj_factor": af,
                "is_suspended": ts_code in sus_set,
                "is_limit_up": limit_flag == "U",
                "is_limit_down": limit_flag == "D",
                "close_adj": (r.get("close") or 0) * af,
            }
        )
    repo.upsert_ods_daily(rows)


def dedup_raw_records(records: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for r in records:
        key = (r.get("api_name"), r.get("ts_code"), r.get("trade_date"), r.get("announce_time"), r.get("data_version"))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out
