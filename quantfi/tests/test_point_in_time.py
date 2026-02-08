from quantfi.features.feature_engine import build_features


class Repo:
    def __init__(self):
        self.rows = []

    def load_recent_bars(self, trade_date: str, lookback: int = 30):
        return [
            {"ts_code": "000001.SZ", "trade_date": "2025-01-02", "close": 10, "close_adj": 10, "is_suspended": False, "is_limit_up": False, "is_limit_down": False},
            {"ts_code": "000001.SZ", "trade_date": "2025-01-03", "close": 11, "close_adj": 11, "is_suspended": False, "is_limit_up": False, "is_limit_down": False},
            {"ts_code": "000001.SZ", "trade_date": "2025-01-04", "close": 99, "close_adj": 99, "is_suspended": False, "is_limit_up": False, "is_limit_down": False},
        ]

    def load_universe(self, trade_date: str):
        return ["000001.SZ"]

    def upsert_features(self, rows):
        self.rows = rows


def test_point_in_time_filters_future_rows():
    repo = Repo()
    build_features(repo, "2025-01-03", "feature_v1")
    assert len(repo.rows) == 1
    payload = repo.rows[0]["payload"]
    assert abs(payload["ret_1d"] - 0.1) < 1e-12
