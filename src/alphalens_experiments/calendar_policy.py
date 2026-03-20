from __future__ import annotations

import pandas as pd


def filter_weekday_rows(prices: pd.DataFrame) -> pd.DataFrame:
    """Keep weekday rows only (Mon-Fri) for JP equity preprocessing baseline."""
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices index must be DatetimeIndex")
    return prices.loc[prices.index.dayofweek < 5].sort_index()


def drop_dates_with_any_missing(prices: pd.DataFrame) -> pd.DataFrame:
    """Drop dates where at least one asset has missing price."""
    return prices.dropna(axis=0, how="any")


def apply_jp_price_policy(prices: pd.DataFrame) -> pd.DataFrame:
    """Apply baseline JP-equity price policy used by this repository.

    Policy:
    1. Keep weekdays only.
    2. Drop dates that contain missing values in any asset.
    """
    weekday_only = filter_weekday_rows(prices)
    return drop_dates_with_any_missing(weekday_only)
