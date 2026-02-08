from __future__ import annotations

from quantfi.core.config import Settings, Versions
from quantfi.core.models import DecisionOutput

def decide(repo: WarehouseRepo, trade_date: str, run_id: str, versions: Versions, settings: Settings, confidence_penalty: float = 0.0) -> list[DecisionOutput]:
    feats = repo.load_features(trade_date, versions.feature_version)
    outputs: list[DecisionOutput] = []
    for row in sorted(feats, key=lambda x: x["ts_code"]):
        p = row["payload"]
        trend = float(p.get("trend_ma5", 0.0))
        ret1d = float(p.get("ret_1d", 0.0))
        score = 0.7 * trend + 0.3 * ret1d
        top_factors = [f"trend_ma5={trend:.4f}", f"ret_1d={ret1d:.4f}"]
        risks = []

        action = "HOLD"
        if score >= settings.decision_threshold_buy:
            action = "BUY"
        elif score <= settings.decision_threshold_sell:
            action = "SELL"

        if p.get("is_suspended"):
            action = "HOLD"
            risks.append("suspended")
        if p.get("is_limit_down") and action == "SELL":
            action = "HOLD"
            risks.append("limit_down_untradable")
        if p.get("is_limit_up") and action == "BUY":
            action = "HOLD"
            risks.append("limit_up_untradable")

        confidence = max(0.0, min(1.0, 0.7 - confidence_penalty - 0.3 * len(risks)))
        outputs.append(
            DecisionOutput(
                ts_code=row["ts_code"],
                trade_date=trade_date,
                action=action,
                score=score,
                confidence=confidence,
                top_factors=top_factors,
                top_risks=risks,
                evidence_links=[],
                reason="no_news_api_in_mvp",
            )
        )

    repo.insert_decisions(
        [
            {
                "trade_date": o.trade_date,
                "ts_code": o.ts_code,
                "payload": {
                    "action": o.action,
                    "score": o.score,
                    "confidence": o.confidence,
                    "top_factors": o.top_factors,
                    "top_risks": o.top_risks,
                    "evidence_links": o.evidence_links,
                    "evidence_reason": o.reason,
                },
                "versions": versions.__dict__,
                "run_id": run_id,
            }
            for o in outputs
        ]
    )
    return outputs
