from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from alphalens_experiments.calendar_policy import (
    apply_jp_price_policy,
    drop_dates_with_any_missing,
    filter_holiday_rows,
    filter_weekday_rows,
    load_holidays_csv,
)


def test_filter_weekday_rows_drops_weekend() -> None:
    index = pd.to_datetime(["2025-01-03", "2025-01-04", "2025-01-06"])
    prices = pd.DataFrame({"7203.T": [100.0, 101.0, 102.0]}, index=index)

    filtered = filter_weekday_rows(prices)

    assert list(filtered.index.strftime("%Y-%m-%d")) == ["2025-01-03", "2025-01-06"]


def test_filter_holiday_rows_drops_configured_dates() -> None:
    index = pd.to_datetime(["2025-01-03", "2025-01-06", "2025-01-07"])
    prices = pd.DataFrame({"7203.T": [100.0, 101.0, 102.0]}, index=index)

    filtered = filter_holiday_rows(prices, holidays=[pd.Timestamp("2025-01-06")])

    assert list(filtered.index.strftime("%Y-%m-%d")) == ["2025-01-03", "2025-01-07"]


def test_drop_dates_with_any_missing_removes_partial_rows() -> None:
    index = pd.to_datetime(["2025-01-06", "2025-01-07"])
    prices = pd.DataFrame(
        {
            "7203.T": [100.0, 101.0],
            "6758.T": [200.0, None],
        },
        index=index,
    )

    dropped = drop_dates_with_any_missing(prices)

    assert list(dropped.index.strftime("%Y-%m-%d")) == ["2025-01-06"]


def test_apply_jp_price_policy_combines_weekday_holiday_and_missing_rules() -> None:
    index = pd.to_datetime(["2025-01-03", "2025-01-04", "2025-01-06", "2025-01-07"])
    prices = pd.DataFrame(
        {
            "7203.T": [100.0, 101.0, 102.0, 103.0],
            "6758.T": [200.0, 201.0, 202.0, None],
        },
        index=index,
    )

    normalized = apply_jp_price_policy(prices, holidays=[pd.Timestamp("2025-01-06")])

    assert list(normalized.index.strftime("%Y-%m-%d")) == ["2025-01-03"]


def test_load_holidays_csv_reads_date_column(tmp_path: Path) -> None:
    path = tmp_path / "jpx_holidays.csv"
    pd.DataFrame({"date": ["2025-01-01", "2025-01-13"]}).to_csv(path, index=False)

    holidays = load_holidays_csv(path)

    assert pd.Timestamp("2025-01-01") in holidays
    assert pd.Timestamp("2025-01-13") in holidays


def test_load_holidays_csv_requires_date_column(tmp_path: Path) -> None:
    path = tmp_path / "invalid_holidays.csv"
    pd.DataFrame({"holiday": ["2025-01-01"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="holiday csv must contain 'date' column"):
        load_holidays_csv(path)
