from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from alphalens_experiments.data_loader import load_factor, load_prices


def test_load_prices_converts_datetime_index_and_sorts(tmp_path: Path) -> None:
    path = tmp_path / "prices.parquet"
    frame = pd.DataFrame(
        {"7203.T": [100.0, 101.0], "6758.T": [200.0, 201.0]},
        index=["2025-01-02", "2025-01-01"],
    )
    frame.to_parquet(path)

    loaded = load_prices(str(path))

    assert isinstance(loaded.index, pd.DatetimeIndex)
    assert list(loaded.index.strftime("%Y-%m-%d")) == ["2025-01-01", "2025-01-02"]


def test_load_prices_reads_csv_with_datetime_index(tmp_path: Path) -> None:
    path = tmp_path / "prices.csv"
    frame = pd.DataFrame(
        {"date": ["2025-01-02", "2025-01-01"], "7203.T": [100.0, 101.0], "6758.T": [200.0, 201.0]}
    )
    frame.to_csv(path, index=False)

    loaded = load_prices(str(path))

    assert isinstance(loaded.index, pd.DatetimeIndex)
    assert loaded.columns.tolist() == ["7203.T", "6758.T"]
    assert list(loaded.index.strftime("%Y-%m-%d")) == ["2025-01-01", "2025-01-02"]


def test_load_factor_from_columns_builds_multiindex_series(
    tmp_path: Path,
) -> None:
    path = tmp_path / "factor_columns.parquet"
    frame = pd.DataFrame(
        {
            "date": ["2025-01-02", "2025-01-01"],
            "asset": [7203, 6758],
            "factor": [0.2, 0.1],
        }
    )
    frame.to_parquet(path)

    loaded = load_factor(str(path))

    assert isinstance(loaded, pd.Series)
    assert isinstance(loaded.index, pd.MultiIndex)
    assert loaded.index.names == ["date", "asset"]
    assert loaded.index[0] == (pd.Timestamp("2025-01-01"), "6758")
    assert loaded.index[1] == (pd.Timestamp("2025-01-02"), "7203")


def test_load_factor_raises_when_required_columns_are_missing(
    tmp_path: Path,
) -> None:
    path = tmp_path / "factor_missing.parquet"
    frame = pd.DataFrame({"date": ["2025-01-01"], "asset": ["7203.T"]})
    frame.to_parquet(path)

    with pytest.raises(ValueError, match="factor file must contain columns"):
        load_factor(str(path))
