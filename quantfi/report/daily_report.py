from __future__ import annotations

from pathlib import Path

from quantfi.core.models import DecisionOutput


def generate_daily_report(trade_date: str, decisions: list[DecisionOutput], out_dir: str = "reports") -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    p = Path(out_dir) / f"daily_{trade_date}.md"
    lines = [f"# Daily Report {trade_date}", "", "| ts_code | action | score | confidence | risks |", "|---|---|---:|---:|---|"]
    for d in decisions:
        lines.append(f"| {d.ts_code} | {d.action} | {d.score:.4f} | {d.confidence:.2f} | {', '.join(d.top_risks)} |")
    p.write_text("\n".join(lines), encoding="utf-8")
    return str(p)
