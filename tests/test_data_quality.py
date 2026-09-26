import pandas as pd
from backend.data.normalize import normalize_ohlcv
from backend.data.quality import quality_report


def test_normalization_removes_duplicates_and_sorts():
    raw=pd.DataFrame({
        "date":["2024-01-02","2024-01-01","2024-01-02"],
        "open":[2,1,2],"high":[3,2,3],"low":[1,0,1],"close":[2,1,2],"volume":[100,200,100]
    })
    out=normalize_ohlcv(raw)
    assert len(out)==2
    assert out["date"].is_monotonic_increasing


def test_quality_report_has_expected_fields():
    df=pd.DataFrame({"date":pd.date_range("2024-01-01",periods=5),"open":[1]*5,"high":[2]*5,"low":[1]*5,"close":[1]*5,"volume":[10]*5})
    report=quality_report(df)
    assert 0 <= report["score"] <= 1
    assert report["rows"]==5
