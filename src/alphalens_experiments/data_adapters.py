from __future__ import annotations

from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from io import StringIO
import json
import os
from pathlib import Path
import random
from typing import Protocol
import sqlite3
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


class PriceDataAdapter(Protocol):
    """Interface for loading raw price data."""

    def load_prices(self) -> pd.DataFrame:
        """Return wide-form price table indexed by datetime."""


DEFAULT_RETRY_POLICY: dict[str, dict[str, object]] = {
    "stooq": {
        "retryable_http_statuses": [429, 500, 502, 503, 504],
        "use_retry_after": False,
        "use_jitter": False,
    },
    "httpcsv": {
        "retryable_http_statuses": [429, 500, 502, 503, 504],
        "use_retry_after": True,
        "use_jitter": True,
    },
}

RETRY_POLICY_SCHEMA: dict[str, object] = {
    "type": "object",
    "patternProperties": {
        "^.+$": {
            "type": "object",
            "properties": {
                "retryable_http_statuses": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 100, "maximum": 599},
                },
                "use_retry_after": {"type": "boolean"},
                "use_jitter": {"type": "boolean"},
            },
            "additionalProperties": False,
            "minProperties": 1,
        }
    },
    "additionalProperties": False,
}


def _clone_retry_policy(
    policy: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    cloned: dict[str, dict[str, object]] = {}
    for provider, values in policy.items():
        cloned_values: dict[str, object] = {}
        for key, value in values.items():
            if isinstance(value, list):
                cloned_values[key] = list(value)
            else:
                cloned_values[key] = value
        cloned[provider] = cloned_values
    return cloned


def _retry_policy_path() -> Path:
    configured = os.getenv("ALPHALENS_RETRY_POLICY_PATH")
    if configured:
        return Path(configured)
    return Path("configs/api_retry_policy.json")


def _load_retry_policy() -> dict[str, dict[str, object]]:
    path = _retry_policy_path()
    if not path.exists():
        return _clone_retry_policy(DEFAULT_RETRY_POLICY)

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"failed to read retry policy config: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"retry policy config is not valid json: {path}") from exc

    if not isinstance(loaded, dict):
        raise RuntimeError(f"retry policy config root must be object: {path}")

    _validate_retry_policy_schema(loaded, path=path)

    merged = _clone_retry_policy(DEFAULT_RETRY_POLICY)
    for provider, policy in loaded.items():
        assert isinstance(provider, str)
        assert isinstance(policy, dict)
        merged_base = merged.get(provider, {})
        merged_base.update(policy)
        merged[provider] = merged_base
    return merged


def _validate_retry_policy_schema(payload: dict[str, object], *, path: Path) -> None:
    validator = Draft202012Validator(RETRY_POLICY_SCHEMA)
    errors = sorted(validator.iter_errors(payload), key=lambda err: err.json_path)
    if not errors:
        return

    first: ValidationError = errors[0]
    raise RuntimeError(
        f"retry policy config schema validation failed: path={path} at={first.json_path} msg={first.message}"
    )


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
    """Load prices from HTTP APIs."""

    provider_name: str
    symbols: tuple[str, ...]
    api_url: str | None = None
    start: str | None = None
    end: str | None = None
    auth_token: str | None = None
    auth_header_name: str = "Authorization"
    auth_header_prefix: str = "Bearer "
    max_retries: int = 2
    retry_wait_seconds: float = 0.5
    retry_jitter_ratio: float = 0.1
    timeout_seconds: float = 10.0

    def load_prices(self) -> pd.DataFrame:
        provider = self.provider_name.lower().strip()

        if provider == "stooq":
            return self._load_stooq_prices()

        if provider == "httpcsv":
            return self._load_http_csv_prices()

        raise ValueError(f"unsupported api provider: {self.provider_name}")

    def _load_stooq_prices(self) -> pd.DataFrame:
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

    def _load_http_csv_prices(self) -> pd.DataFrame:
        if self.api_url is None:
            raise ValueError("provider=httpcsv requires --api-url")
        if not self.symbols:
            raise ValueError("provider=httpcsv requires --symbols")
        if self.auth_token is None:
            raise ValueError("provider=httpcsv requires auth token")

        if "{symbol}" in self.api_url:
            series_list: list[pd.Series] = []
            for symbol in self.symbols:
                url = self.api_url.replace("{symbol}", symbol)
                frame = self._read_csv_from_url(url)
                series_list.append(self._coerce_symbol_close_series(frame, symbol))
            prices = pd.concat(series_list, axis=1)
            prices.columns = list(self.symbols)
            return _normalize_wide_prices(prices)

        frame = self._read_csv_from_url(self.api_url)
        prices = _coerce_long_to_wide(frame)
        if self.start is not None:
            prices = prices.loc[pd.Timestamp(self.start) :]
        if self.end is not None:
            prices = prices.loc[: pd.Timestamp(self.end)]
        return _normalize_wide_prices(prices)

    def _coerce_symbol_close_series(self, frame: pd.DataFrame, symbol: str) -> pd.Series:
        lowered = {column.lower(): column for column in frame.columns}

        if "date" not in lowered:
            raise ValueError(f"httpcsv response must contain date column. symbol={symbol}")

        date_col = lowered["date"]
        close_col = lowered.get("close")
        if close_col is None:
            raise ValueError(f"httpcsv response must contain close column. symbol={symbol}")

        series = pd.Series(
            pd.to_numeric(frame[close_col], errors="coerce").to_numpy(),
            index=pd.to_datetime(frame[date_col]),
            name=symbol,
        ).dropna()
        return series.sort_index()

    def _fetch_stooq_close_series(self, symbol: str) -> pd.Series:
        query = urlencode({"s": self._to_stooq_symbol(symbol), "i": "d"})
        url = f"https://stooq.com/q/d/l/?{query}"

        frame = self._read_csv_from_url(url)
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

    def _read_csv_from_url(self, url: str) -> pd.DataFrame:
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                request = Request(url, headers=self._build_headers())
                with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                    payload = response.read().decode("utf-8")
                frame = pd.read_csv(StringIO(payload))
                if frame.empty:
                    raise ValueError(f"empty response. url={url}")
                return frame
            except HTTPError as exc:
                last_error = exc
                if attempt >= self.max_retries or not self._is_retryable_http_error(exc):
                    break
                time.sleep(self._retry_delay_seconds(exc, attempt))
            except URLError as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(self._backoff_seconds(attempt))
            except ValueError as exc:
                last_error = exc
                if attempt >= self.max_retries or not self._is_retryable_value_error(exc):
                    break
                time.sleep(self._backoff_seconds(attempt))

        assert last_error is not None
        raise RuntimeError(f"failed to fetch prices from url={url}: {last_error}") from last_error

    @staticmethod
    def _is_retryable_value_error(exc: ValueError) -> bool:
        message = str(exc).lower()
        return "empty response" in message

    def _backoff_seconds(self, attempt: int) -> float:
        base_seconds = self.retry_wait_seconds * (2**attempt)
        return self._apply_jitter(base_seconds)

    def _retry_delay_seconds(self, exc: HTTPError, attempt: int) -> float:
        if not self._provider_uses_retry_after():
            return self._backoff_seconds(attempt)

        headers = exc.headers
        if headers is None:
            return self._backoff_seconds(attempt)

        retry_after = headers.get("Retry-After")
        if retry_after is None:
            return self._backoff_seconds(attempt)

        try:
            retry_after_seconds = float(retry_after)
        except ValueError:
            parsed_seconds = self._retry_after_http_date_seconds(retry_after)
            if parsed_seconds is None:
                return self._backoff_seconds(attempt)
            return parsed_seconds

        return max(0.0, retry_after_seconds)

    @staticmethod
    def _retry_after_http_date_seconds(value: str) -> float | None:
        try:
            retry_after_dt = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if retry_after_dt is None:
            return None

        # parsedate_to_datetime can return naive dt for some formats.
        retry_after_ts = retry_after_dt.timestamp()
        return max(0.0, retry_after_ts - time.time())

    def _apply_jitter(self, seconds: float) -> float:
        if not self._provider_uses_jitter():
            return seconds

        ratio = self.retry_jitter_ratio
        if ratio <= 0.0:
            return seconds
        lower = max(0.0, seconds * (1.0 - ratio))
        upper = seconds * (1.0 + ratio)
        return random.uniform(lower, upper)

    def _provider_uses_retry_after(self) -> bool:
        return bool(self._provider_policy().get("use_retry_after", False))

    def _provider_uses_jitter(self) -> bool:
        return bool(self._provider_policy().get("use_jitter", False))

    def _provider_policy(self) -> dict[str, object]:
        provider = self.provider_name.lower().strip()
        policies = _load_retry_policy()
        return policies.get(provider, DEFAULT_RETRY_POLICY.get(provider, {}))

    def _is_retryable_http_error(self, exc: HTTPError) -> bool:
        statuses = self._provider_policy().get("retryable_http_statuses", [])
        if not isinstance(statuses, list):
            return False
        try:
            allowed = {int(status) for status in statuses}
        except (TypeError, ValueError):
            return False
        return exc.code in allowed

    def _build_headers(self) -> dict[str, str]:
        if self.auth_token is None:
            return {}
        return {self.auth_header_name: f"{self.auth_header_prefix}{self.auth_token}"}

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
    api_url: str | None = None,
    start: str | None = None,
    end: str | None = None,
    auth_token: str | None = None,
    auth_header_name: str = "Authorization",
    auth_header_prefix: str = "Bearer ",
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
            api_url=api_url,
            start=start,
            end=end,
            auth_token=auth_token,
            auth_header_name=auth_header_name,
            auth_header_prefix=auth_header_prefix,
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
