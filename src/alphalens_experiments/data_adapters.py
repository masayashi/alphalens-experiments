from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Protocol
import sqlite3
import time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


class PriceDataAdapter(Protocol):
    """Interface for loading raw price data."""

    def load_prices(self) -> pd.DataFrame:
        """Return wide-form price table indexed by datetime."""


def _normalize_wide_prices(prices: pd.DataFrame) -> pd.DataFrame:
    normalized = prices.copy()
    if not isinstance(normalized.index, pd.DatetimeIndex):
        normalized.index = pd.to_datetime(normalized.index)
    normalized.index = normalized.index.normalize()
    normalized.columns = normalized.columns.astype(str)
    return normalized.sort_index()


def _coerce_long_to_wide(frame: pd.DataFrame) -> pd.DataFrame:
    lowered = {column.lower(): column for column in frame.columns}
    required = {"date", "asset", "close"}

    if required.issubset(lowered):
        date_col = lowered["date"]
        asset_col = lowered["asset"]
        close_col = lowered["close"]
        wide = (
            frame.assign(
                date=lambda x: pd.to_datetime(x[date_col]),
                asset=lambda x: x[asset_col].astype(str),
                close=lambda x: pd.to_numeric(x[close_col], errors="coerce"),
            )
            .pivot(index="date", columns="asset", values="close")
            .sort_index()
        )
        return _normalize_wide_prices(wide)

    if "date" in lowered:
        date_col = lowered["date"]
        wide = frame.rename(columns={date_col: "date"}).set_index("date")
        numeric_columns = wide.columns
        wide[numeric_columns] = wide[numeric_columns].apply(pd.to_numeric, errors="coerce")
        return _normalize_wide_prices(wide)

    raise ValueError("price data must be long(date,asset,close) or wide(date + ticker columns)")


@dataclass(frozen=True)
class CsvPriceAdapter:
    """Load prices from local CSV (long or wide format)."""

    path: str

    def load_prices(self) -> pd.DataFrame:
        frame = pd.read_csv(self.path)
        return _coerce_long_to_wide(frame)


@dataclass(frozen=True)
class ApiPriceAdapter:
    """Load prices from public HTTP APIs."""

    provider_name: str
    symbols: tuple[str, ...]
    start: str | None = None
    end: str | None = None
    max_retries: int = 2
    retry_wait_seconds: float = 0.5
    timeout_seconds: float = 10.0

    def load_prices(self) -> pd.DataFrame:
        provider = self.provider_name.lower().strip()
        if provider != "stooq":
            raise ValueError(f"unsupported api provider: {self.provider_name}")
        if not self.symbols:
            raise ValueError("api adapter requires at least one symbol")

        frames: list[pd.Series] = []
        for symbol in self.symbols:
            frames.append(self._fetch_stooq_close_series(symbol))

        prices = pd.concat(frames, axis=1)
        prices.columns = list(self.symbols)
        if self.start is not None:
            prices = prices.loc[pd.Timestamp(self.start) :]
        if self.end is not None:
            prices = prices.loc[: pd.Timestamp(self.end)]
        return _normalize_wide_prices(prices)

    def _fetch_stooq_close_series(self, symbol: str) -> pd.Series:
        query = urlencode({"s": self._to_stooq_symbol(symbol), "i": "d"})
        url = f"https://stooq.com/q/d/l/?{query}"

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(url, timeout=self.timeout_seconds) as response:  # noqa: S310
                    payload = response.read().decode("utf-8")
                frame = pd.read_csv(StringIO(payload))
                if frame.empty:
                    raise ValueError(f"empty response for symbol={symbol}")
                if "Date" not in frame.columns or "Close" not in frame.columns:
                    raise ValueError(f"invalid stooq response columns for symbol={symbol}")

                series = pd.Series(
                    pd.to_numeric(frame["Close"], errors="coerce").to_numpy(),
                    index=pd.to_datetime(frame["Date"]),
                    name=symbol,
                ).dropna()
                return series.sort_index()
            except (URLError, ValueError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(self.retry_wait_seconds)

        assert last_error is not None
        raise RuntimeError(
            f"failed to fetch stooq prices for symbol={symbol}: {last_error}"
        ) from last_error

    @staticmethod
    def _to_stooq_symbol(symbol: str) -> str:
        normalized = symbol.strip().lower()
        if normalized.endswith(".t"):
            return f"{normalized[:-2]}.jp"
        return normalized


@dataclass(frozen=True)
class DatabasePriceAdapter:
    """Load prices from SQLite query results."""

    dsn: str
    query: str

    def load_prices(self) -> pd.DataFrame:
        db_path = self._parse_sqlite_path(self.dsn)
        connection = sqlite3.connect(db_path)
        try:
            frame = pd.read_sql_query(self.query, connection)
        finally:
            connection.close()

        if frame.empty:
            raise ValueError("database query returned no rows")
        return _coerce_long_to_wide(frame)

    @staticmethod
    def _parse_sqlite_path(dsn: str) -> str:
        prefix = "sqlite:///"
        if not dsn.startswith(prefix):
            raise ValueError("dsn must start with sqlite:///")
        return dsn[len(prefix) :]


def build_adapter(
    source: str,
    *,
    path: str | None = None,
    provider: str | None = None,
    symbols: tuple[str, ...] = (),
    start: str | None = None,
    end: str | None = None,
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
        if not symbols:
            raise ValueError("source=api requires --symbols")
        return ApiPriceAdapter(
            provider_name=provider,
            symbols=symbols,
            start=start,
            end=end,
        )

    if source == "db":
        if dsn is None or query is None:
            raise ValueError("source=db requires --dsn and --query")
        return DatabasePriceAdapter(dsn=dsn, query=query)

    raise ValueError(f"unsupported source: {source}")


def save_loaded_prices(prices: pd.DataFrame, out_path: str) -> Path:
    """Persist loaded prices as raw CSV for downstream processing."""
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(target, index_label="date")
    return target
