from quantfi.ingest.pipeline import dedup_raw_records


def test_dedup_records():
    rec = {"api_name": "daily", "ts_code": "000001.SZ", "trade_date": "20250101", "announce_time": None, "payload": {"a": 1}, "data_version": "v1"}
    out = dedup_raw_records([rec, rec.copy()])
    assert len(out) == 1
