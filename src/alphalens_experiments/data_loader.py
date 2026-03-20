from __future__ import annotations

import pandas as pd


def load_prices(path: str) -> pd.DataFrame:
    """Load wide-form prices DataFrame indexed by datetime."""
    prices = pd.read_parquet(path)
    if not isinstance(prices.index, pd.DatetimeIndex):
        prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index()
    return prices


def load_factor(path: str) -> pd.Series:
    """Load factor values as a MultiIndex Series (datetime, asset)."""
    factor_frame = pd.read_parquet(path)

    if isinstance(factor_frame.index, pd.MultiIndex):
        series = factor_frame.squeeze()
        series.index = pd.MultiIndex.from_tuples(
            [
                (pd.Timestamp(level0), str(level1))
                for level0, level1 in series.index.to_list()
            ],
            names=["date", "asset"],
        )
    else:
        required_cols = {"date", "asset", "factor"}
        missing = required_cols - set(factor_frame.columns)
        if missing:
            raise ValueError(f"factor file must contain columns {required_cols}, missing={missing}")
        series = factor_frame.assign(date=lambda x: pd.to_datetime(x["date"])).set_index(
            ["date", "asset"]
        )["factor"]

    return series.sort_index()

