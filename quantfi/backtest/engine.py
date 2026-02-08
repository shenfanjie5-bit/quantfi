from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BacktestResult:
    total_return: float
    annualized_return: float
    win_rate: float
    trades: int


def run_backtest(decision_by_date: dict[str, list[dict]], returns_by_date: dict[str, dict[str, float]], cost_bps: float = 5.0) -> BacktestResult:
    pnl = []
    wins = 0
    trades = 0
    for d in sorted(decision_by_date.keys()):
        day_ret = 0.0
        for rec in decision_by_date[d]:
            r = returns_by_date.get(d, {}).get(rec["ts_code"], 0.0)
            if rec["action"] == "BUY":
                day_ret += r - cost_bps / 10000
                trades += 1
            elif rec["action"] == "SELL":
                day_ret += -r - cost_bps / 10000
                trades += 1
        pnl.append(day_ret)
        if day_ret > 0:
            wins += 1
    total = 1.0
    for r in pnl:
        total *= 1 + r
    total_return = total - 1
    periods = max(1, len(pnl))
    annualized = total ** (252 / periods) - 1
    win_rate = wins / periods
    return BacktestResult(total_return=total_return, annualized_return=annualized, win_rate=win_rate, trades=trades)
