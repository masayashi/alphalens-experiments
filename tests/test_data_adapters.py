from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from alphalens_experiments.data_adapters import (
    ApiPriceAdapter,
    CsvPriceAdapter,
    DatabasePriceAdapter,
    build_adapter,
)


def test_csv_price_adapter_loads_and_sorts_prices(tmp_path: Path) -> None:
    path = tmp_path / "prices.csv"
    frame = pd.DataFrame(
        {
            "date": ["2025-01-02", "2025-01-01"],
            "7203.T": [100.0, 101.0],
            "6758.T": [200.0, 201.0],
        }
    )
    frame.to_csv(path, index=False)

    loaded = CsvPriceAdapter(path=str(path)).load_prices()

    assert list(loaded.index.strftime("%Y-%m-%d")) == ["2025-01-01", "2025-01-02"]
    assert loaded.columns.tolist() == ["7203.T", "6758.T"]


def test_api_adapter_is_placeholder() -> None:
    with pytest.raises(NotImplementedError, match="API adapter is not implemented yet"):
        ApiPriceAdapter(provider_name="example").load_prices()


def test_db_adapter_is_placeholder() -> None:
    with pytest.raises(NotImplementedError, match="Database adapter is not implemented yet"):
        DatabasePriceAdapter(dsn="sqlite://", query="SELECT 1").load_prices()


def test_build_adapter_requires_parameters() -> None:
    with pytest.raises(ValueError, match="source=csv requires --path"):
        build_adapter(source="csv")
