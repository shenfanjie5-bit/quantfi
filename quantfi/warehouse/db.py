from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy import create_engine, text


DDL = """
CREATE TABLE IF NOT EXISTS run_log (
    run_id TEXT PRIMARY KEY,
    task TEXT NOT NULL,
    trade_date DATE NOT NULL,
    status TEXT NOT NULL,
    confidence_penalty DOUBLE PRECISION NOT NULL DEFAULT 0,
    degradation_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    versions JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw_tushare (
    id BIGSERIAL PRIMARY KEY,
    api_name TEXT NOT NULL,
    ts_code TEXT,
    trade_date DATE,
    announce_time TIMESTAMPTZ,
    payload JSONB NOT NULL,
    ingest_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_version TEXT NOT NULL,
    UNIQUE (api_name, ts_code, trade_date, announce_time, data_version)
);

CREATE TABLE IF NOT EXISTS ods_daily_bar (
    ts_code TEXT NOT NULL,
    trade_date DATE NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    vol DOUBLE PRECISION,
    amount DOUBLE PRECISION,
    adj_factor DOUBLE PRECISION,
    is_suspended BOOLEAN DEFAULT FALSE,
    is_limit_up BOOLEAN DEFAULT FALSE,
    is_limit_down BOOLEAN DEFAULT FALSE,
    close_adj DOUBLE PRECISION,
    PRIMARY KEY (ts_code, trade_date)
);

CREATE TABLE IF NOT EXISTS universe_snapshot (
    trade_date DATE NOT NULL,
    ts_code TEXT NOT NULL,
    source TEXT NOT NULL,
    reason TEXT,
    PRIMARY KEY (trade_date, ts_code)
);

CREATE TABLE IF NOT EXISTS feature_daily (
    trade_date DATE NOT NULL,
    ts_code TEXT NOT NULL,
    feature_version TEXT NOT NULL,
    payload JSONB NOT NULL,
    as_of_time TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (trade_date, ts_code, feature_version)
);

CREATE TABLE IF NOT EXISTS decision_daily (
    trade_date DATE NOT NULL,
    ts_code TEXT NOT NULL,
    payload JSONB NOT NULL,
    versions JSONB NOT NULL,
    run_id TEXT NOT NULL,
    PRIMARY KEY (trade_date, ts_code, run_id)
);
"""


class DB:
    def __init__(self, url: str):
        self.engine = create_engine(url, future=True)

    def init_db(self) -> None:
        with self.engine.begin() as conn:
            for stmt in DDL.strip().split(";\n\n"):
                if stmt.strip():
                    conn.execute(text(stmt))

    @contextmanager
    def begin(self):
        with self.engine.begin() as conn:
            yield conn
