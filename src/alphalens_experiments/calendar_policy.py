from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd


def filter_weekday_rows(prices: pd.DataFrame) -> pd.DataFrame:
    """Keep weekday rows only (Mon-Fri) for JP equity preprocessing baseline."""
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices index must be DatetimeIndex")
    return prices.loc[prices.index.dayofweek < 5].sort_index()


def drop_dates_with_any_missing(prices: pd.DataFrame) -> pd.DataFrame:
    """Drop dates where at least one asset has missing price."""
    return prices.dropna(axis=0, how="any")


def load_holidays_csv(path: str | Path) -> set[pd.Timestamp]:
    """Load holiday dates from CSV with required `date` column."""
    frame = pd.read_csv(path)
    lowered = {column.lower(): column for column in frame.columns}

    if "date" not in lowered:
        raise ValueError("holiday csv must contain 'date' column")

    date_col = lowered["date"]
    holidays = pd.to_datetime(frame[date_col]).dt.normalize()
    return set(pd.Timestamp(d) for d in holidays)


def filter_holiday_rows(prices: pd.DataFrame, holidays: Iterable[pd.Timestamp]) -> pd.DataFrame:
    """Drop rows that match configured holiday dates."""
    holiday_set = {pd.Timestamp(day).normalize() for day in holidays}
    if not holiday_set:
        return prices

    normalized_index = prices.index.normalize()
    keep_mask = ~normalized_index.isin(holiday_set)
    return prices.loc[keep_mask].sort_index()


def apply_jp_price_policy(
    prices: pd.DataFrame,
    holidays: Iterable[pd.Timestamp] | None = None,
) -> pd.DataFrame:
    """Apply JP-equity price policy used by this repository.

    Policy:
    1. Keep weekdays only.
    2. Optionally drop configured holiday dates.
    3. Drop dates that contain missing values in any asset.
    """
    weekday_only = filter_weekday_rows(prices)
    holiday_filtered = filter_holiday_rows(weekday_only, holidays or [])
    return drop_dates_with_any_missing(holiday_filtered)
