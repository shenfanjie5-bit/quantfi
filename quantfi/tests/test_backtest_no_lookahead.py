from quantfi.backtest.engine import run_backtest


def test_backtest_no_lookahead_same_day_mapping_only():
    decisions = {
        "2025-01-02": [{"ts_code": "000001.SZ", "action": "BUY"}],
    }
    returns = {
        "2025-01-03": {"000001.SZ": 0.2},
        "2025-01-02": {"000001.SZ": 0.0},
    }
    res = run_backtest(decisions, returns, cost_bps=0)
    assert abs(res.total_return - 0.0) < 1e-9
