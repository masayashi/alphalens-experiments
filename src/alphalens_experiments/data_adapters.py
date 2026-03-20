from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd


class PriceDataAdapter(Protocol):
    """Interface for loading raw price data."""

    def load_prices(self) -> pd.DataFrame:
        """Return wide-form price table indexed by datetime."""


@dataclass(frozen=True)
class CsvPriceAdapter:
    """Load prices from local CSV (date + ticker columns)."""

    path: str

    def load_prices(self) -> pd.DataFrame:
        frame = pd.read_csv(self.path)
        lowered = {column.lower(): column for column in frame.columns}

        if "date" not in lowered:
            raise ValueError("csv adapter requires a 'date' column")

        date_col = lowered["date"]
        prices = frame.rename(columns={date_col: "date"}).set_index("date")
        prices.index = pd.to_datetime(prices.index)
        prices.columns = prices.columns.astype(str)
        return prices.sort_index()


@dataclass(frozen=True)
class ApiPriceAdapter:
    """Placeholder adapter for external market data API."""

    provider_name: str

    def load_prices(self) -> pd.DataFrame:
        raise NotImplementedError(
            f"API adapter is not implemented yet. provider={self.provider_name}. "
            "Implement request/auth/rate-limit handling here."
        )


@dataclass(frozen=True)
class DatabasePriceAdapter:
    """Placeholder adapter for database-backed price retrieval."""

    dsn: str
    query: str

    def load_prices(self) -> pd.DataFrame:
        raise NotImplementedError(
            "Database adapter is not implemented yet. "
            "Implement connection management and query execution here."
        )


def build_adapter(
    source: str,
    *,
    path: str | None = None,
    provider: str | None = None,
    dsn: str | None = None,
    query: str | None = None,
) -> PriceDataAdapter:
    """Factory for selecting a price adapter by source type."""
    if source == "csv":
        if path is None:
            raise ValueError("source=csv requires --path")
        return CsvPriceAdapter(path=path)

    if source == "api":
        if provider is None:
            raise ValueError("source=api requires --provider")
        return ApiPriceAdapter(provider_name=provider)

    if source == "db":
        if dsn is None or query is None:
            raise ValueError("source=db requires --dsn and --query")
        return DatabasePriceAdapter(dsn=dsn, query=query)

    raise ValueError(f"unsupported source: {source}")


def save_loaded_prices(prices: pd.DataFrame, out_path: str) -> Path:
    """Persist loaded prices as raw CSV for downstream processing."""
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(target)
    return target
