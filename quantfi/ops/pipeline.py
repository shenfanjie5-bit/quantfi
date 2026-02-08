from __future__ import annotations

from datetime import datetime
import uuid

from quantfi.core.config import Settings
from quantfi.core.tushare_client import TuShareClient
from quantfi.core.versioning import build_versions
from quantfi.decision.engine import decide
from quantfi.features.feature_engine import build_features
from quantfi.features.universe import build_universe
from quantfi.ingest.pipeline import ingest_daily
from quantfi.report.daily_report import generate_daily_report
from quantfi.warehouse.db import DB
from quantfi.warehouse.repositories import WarehouseRepo


def run_daily(trade_date: str, settings: Settings) -> dict:
    versions = build_versions(settings)
    run_id = uuid.uuid4().hex
    db = DB(settings.database_url)
    repo = WarehouseRepo(db)
    repo.upsert_run_log(
        {
            "run_id": run_id,
            "task": "run_daily",
            "trade_date": trade_date,
            "status": "running",
            "confidence_penalty": 0.0,
            "degradation_reasons": [],
            "versions": versions.__dict__,
        }
    )

    client = TuShareClient(settings.tushare_token)
    ingest_state = ingest_daily(client, repo, trade_date, versions.data_version)
    build_universe(repo, settings, trade_date)
    build_features(repo, trade_date, versions.feature_version)
    decisions = decide(repo, trade_date, run_id, versions, settings, ingest_state.confidence_penalty)
    report_path = generate_daily_report(trade_date, decisions)

    repo.upsert_run_log(
        {
            "run_id": run_id,
            "task": "run_daily",
            "trade_date": trade_date,
            "status": "success",
            "confidence_penalty": ingest_state.confidence_penalty,
            "degradation_reasons": ingest_state.degrade_reasons,
            "versions": versions.__dict__,
        }
    )
    return {"run_id": run_id, "report": report_path, "degradations": ingest_state.degrade_reasons}
