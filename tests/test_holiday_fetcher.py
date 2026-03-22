from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
import pytest

from alphalens_experiments.holiday_fetcher import (
    fetch_holidays_csv,
    normalize_holidays_dataframe,
)


class _FakeHttpResponse:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload.encode("utf-8")

    def __enter__(self) -> _FakeHttpResponse:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> Literal[False]:
        return False


def test_normalize_holidays_dataframe_supports_japanese_date_column() -> None:
    frame = pd.DataFrame({"日付": ["2025-01-01", "2025-01-13", "2025-01-13"]})

    normalized = normalize_holidays_dataframe(frame)

    assert normalized.columns.tolist() == ["date"]
    assert normalized["date"].tolist() == ["2025-01-01", "2025-01-13"]


def test_normalize_holidays_dataframe_requires_date_column() -> None:
    frame = pd.DataFrame({"holiday": ["2025-01-01"]})

    with pytest.raises(ValueError, match="date column"):
        normalize_holidays_dataframe(frame)


def test_fetch_holidays_csv_downloads_and_saves(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = "date,name\n2025-01-01,New Year\n2025-01-13,Holiday\n"

    def fake_urlopen(url: str, timeout: float = 15.0) -> _FakeHttpResponse:
        assert "example.com" in url
        assert timeout == 15.0
        return _FakeHttpResponse(payload)

    monkeypatch.setattr("alphalens_experiments.holiday_fetcher.urlopen", fake_urlopen)

    out_path = tmp_path / "jpx_holidays_latest.csv"
    saved = fetch_holidays_csv("https://example.com/holidays.csv", out_path)

    assert saved == out_path
    loaded = pd.read_csv(saved)
    assert loaded["date"].tolist() == ["2025-01-01", "2025-01-13"]
