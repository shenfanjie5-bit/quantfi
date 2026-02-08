from quantfi.core.config import Settings, Versions
from quantfi.decision.engine import decide


class Repo:
    def __init__(self):
        self.saved = []

    def load_features(self, trade_date, feature_version):
        return [
            {"ts_code": "600000.SH", "payload": {"trend_ma5": 0.3, "ret_1d": 0.0, "is_suspended": False, "is_limit_down": False, "is_limit_up": False}},
            {"ts_code": "000001.SZ", "payload": {"trend_ma5": -0.3, "ret_1d": 0.0, "is_suspended": False, "is_limit_down": False, "is_limit_up": False}},
        ]

    def insert_decisions(self, rows):
        self.saved = rows


def test_reproducible_output_same_inputs():
    repo = Repo()
    settings = Settings()
    versions = Versions(code_version="c", config_version="k")
    out1 = decide(repo, "2025-01-03", "run1", versions, settings, 0.0)
    out2 = decide(repo, "2025-01-03", "run1", versions, settings, 0.0)
    assert [o.action for o in out1] == [o.action for o in out2]
    assert [o.ts_code for o in out1] == [o.ts_code for o in out2]
