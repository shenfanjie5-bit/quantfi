from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunContext:
    run_id: str
    trade_date: str
    task: str


@dataclass(frozen=True)
class DecisionOutput:
    ts_code: str
    trade_date: str
    action: str
    score: float
    confidence: float
    top_factors: list[str]
    top_risks: list[str]
    evidence_links: list[str]
    reason: str | None = None
