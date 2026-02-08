from __future__ import annotations

import json
from typing import Iterable
from sqlalchemy import text

from quantfi.warehouse.db import DB


class WarehouseRepo:
    def __init__(self, db: DB):
        self.db = db

    def upsert_run_log(self, run: dict) -> None:
        sql = text(
            """
            INSERT INTO run_log(run_id, task, trade_date, status, confidence_penalty, degradation_reasons, versions)
            VALUES (:run_id, :task, :trade_date, :status, :confidence_penalty, CAST(:degradation_reasons AS JSONB), CAST(:versions AS JSONB))
            ON CONFLICT(run_id) DO UPDATE
            SET status=EXCLUDED.status,
                confidence_penalty=EXCLUDED.confidence_penalty,
                degradation_reasons=EXCLUDED.degradation_reasons,
                versions=EXCLUDED.versions,
                updated_at=NOW();
            """
        )
        with self.db.begin() as conn:
            conn.execute(
                sql,
                {
                    **run,
                    "degradation_reasons": json.dumps(run.get("degradation_reasons", []), ensure_ascii=False),
                    "versions": json.dumps(run["versions"], ensure_ascii=False),
                },
            )

    def insert_raw_records(self, records: Iterable[dict]) -> int:
        sql = text(
            """
            INSERT INTO raw_tushare(api_name, ts_code, trade_date, announce_time, payload, data_version)
            VALUES (:api_name, :ts_code, :trade_date, :announce_time, CAST(:payload AS JSONB), :data_version)
            ON CONFLICT DO NOTHING;
            """
        )
        n = 0
        with self.db.begin() as conn:
            for rec in records:
                conn.execute(sql, {**rec, "payload": json.dumps(rec["payload"], ensure_ascii=False)})
                n += 1
        return n

    def upsert_ods_daily(self, rows: Iterable[dict]) -> None:
        sql = text(
            """
            INSERT INTO ods_daily_bar(ts_code, trade_date, open, high, low, close, vol, amount, adj_factor, is_suspended, is_limit_up, is_limit_down, close_adj)
            VALUES (:ts_code, :trade_date, :open, :high, :low, :close, :vol, :amount, :adj_factor, :is_suspended, :is_limit_up, :is_limit_down, :close_adj)
            ON CONFLICT(ts_code, trade_date) DO UPDATE SET
                open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low, close=EXCLUDED.close,
                vol=EXCLUDED.vol, amount=EXCLUDED.amount, adj_factor=EXCLUDED.adj_factor,
                is_suspended=EXCLUDED.is_suspended, is_limit_up=EXCLUDED.is_limit_up, is_limit_down=EXCLUDED.is_limit_down,
                close_adj=EXCLUDED.close_adj;
            """
        )
        with self.db.begin() as conn:
            for row in rows:
                conn.execute(sql, row)

    def replace_universe(self, trade_date: str, rows: list[dict]) -> None:
        with self.db.begin() as conn:
            conn.execute(text("DELETE FROM universe_snapshot WHERE trade_date=:d"), {"d": trade_date})
            sql = text("INSERT INTO universe_snapshot(trade_date, ts_code, source, reason) VALUES (:trade_date,:ts_code,:source,:reason)")
            for row in rows:
                conn.execute(sql, row)

    def upsert_features(self, rows: list[dict]) -> None:
        sql = text(
            """
            INSERT INTO feature_daily(trade_date, ts_code, feature_version, payload, as_of_time)
            VALUES (:trade_date,:ts_code,:feature_version,CAST(:payload AS JSONB),:as_of_time)
            ON CONFLICT(trade_date, ts_code, feature_version) DO UPDATE
            SET payload=EXCLUDED.payload, as_of_time=EXCLUDED.as_of_time;
            """
        )
        with self.db.begin() as conn:
            for row in rows:
                conn.execute(sql, {**row, "payload": json.dumps(row["payload"], ensure_ascii=False)})

    def insert_decisions(self, rows: list[dict]) -> None:
        sql = text(
            """
            INSERT INTO decision_daily(trade_date, ts_code, payload, versions, run_id)
            VALUES (:trade_date,:ts_code,CAST(:payload AS JSONB),CAST(:versions AS JSONB),:run_id)
            ON CONFLICT(trade_date, ts_code, run_id) DO UPDATE
            SET payload=EXCLUDED.payload, versions=EXCLUDED.versions;
            """
        )
        with self.db.begin() as conn:
            for row in rows:
                conn.execute(
                    sql,
                    {
                        **row,
                        "payload": json.dumps(row["payload"], ensure_ascii=False),
                        "versions": json.dumps(row["versions"], ensure_ascii=False),
                    },
                )

    def load_recent_bars(self, trade_date: str, lookback: int = 30) -> list[dict]:
        sql = text(
            """
            SELECT * FROM ods_daily_bar WHERE trade_date <= :trade_date
            ORDER BY trade_date DESC LIMIT :lookback * 5000;
            """
        )
        with self.db.begin() as conn:
            return [dict(r._mapping) for r in conn.execute(sql, {"trade_date": trade_date, "lookback": lookback})]

    def load_universe(self, trade_date: str) -> list[str]:
        sql = text("SELECT ts_code FROM universe_snapshot WHERE trade_date=:d")
        with self.db.begin() as conn:
            return [r[0] for r in conn.execute(sql, {"d": trade_date}).fetchall()]

    def load_features(self, trade_date: str, feature_version: str) -> list[dict]:
        sql = text("SELECT ts_code, payload FROM feature_daily WHERE trade_date=:d AND feature_version=:v")
        with self.db.begin() as conn:
            return [dict(r._mapping) for r in conn.execute(sql, {"d": trade_date, "v": feature_version})]
