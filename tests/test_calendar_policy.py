from __future__ import annotations

import pandas as pd

from alphalens_experiments.calendar_policy import (
    apply_jp_price_policy,
    drop_dates_with_any_missing,
    filter_weekday_rows,
)


def test_filter_weekday_rows_drops_weekend() -> None:
    index = pd.to_datetime(["2025-01-03", "2025-01-04", "2025-01-06"])
    prices = pd.DataFrame({"7203.T": [100.0, 101.0, 102.0]}, index=index)

    filtered = filter_weekday_rows(prices)

    assert list(filtered.index.strftime("%Y-%m-%d")) == ["2025-01-03", "2025-01-06"]


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


def test_apply_jp_price_policy_combines_weekday_and_missing_rules() -> None:
    index = pd.to_datetime(["2025-01-03", "2025-01-04", "2025-01-06"])
    prices = pd.DataFrame(
        {
            "7203.T": [100.0, 101.0, 102.0],
            "6758.T": [200.0, 201.0, None],
        },
        index=index,
    )

    normalized = apply_jp_price_policy(prices)

    assert list(normalized.index.strftime("%Y-%m-%d")) == ["2025-01-03"]
