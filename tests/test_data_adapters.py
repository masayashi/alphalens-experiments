from __future__ import annotations

from pathlib import Path
from typing import Literal
import sqlite3
from urllib.request import Request

import pandas as pd
import pytest

from alphalens_experiments.data_adapters import (
    ApiPriceAdapter,
    CsvPriceAdapter,
    DatabasePriceAdapter,
    build_adapter,
)


class _FakeHttpResponse:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload.encode("utf-8")

    def __enter__(self) -> _FakeHttpResponse:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> Literal[False]:
        return False


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


def test_api_adapter_stooq_loads_prices_with_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    payload_7203 = (
        "Date,Open,High,Low,Close,Volume\n"
        "2025-01-01,100,101,99,100.5,1000\n"
        "2025-01-02,101,102,100,101.5,1200\n"
    )
    payload_6758 = (
        "Date,Open,High,Low,Close,Volume\n"
        "2025-01-01,200,201,199,200.5,900\n"
        "2025-01-02,201,202,200,201.5,1100\n"
    )

    def fake_urlopen(request: Request, timeout: float = 10.0) -> _FakeHttpResponse:
        assert timeout == 10.0
        if "7203.jp" in request.full_url:
            return _FakeHttpResponse(payload_7203)
        if "6758.jp" in request.full_url:
            return _FakeHttpResponse(payload_6758)
        raise AssertionError(f"unexpected url: {request.full_url}")

    monkeypatch.setattr("alphalens_experiments.data_adapters.urlopen", fake_urlopen)

    loaded = ApiPriceAdapter(
        provider_name="stooq",
        symbols=("7203.T", "6758.T"),
        start="2025-01-01",
        end="2025-01-02",
    ).load_prices()

    assert loaded.columns.tolist() == ["7203.T", "6758.T"]
    assert list(loaded.index.strftime("%Y-%m-%d")) == ["2025-01-01", "2025-01-02"]
    assert float(loaded.loc[pd.Timestamp("2025-01-02"), "7203.T"]) == 101.5


def test_api_adapter_httpcsv_uses_auth_header(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = "date,close\n2025-01-01,100.0\n2025-01-02,101.0\n"

    def fake_urlopen(request: Request, timeout: float = 10.0) -> _FakeHttpResponse:
        assert timeout == 10.0
        assert request.full_url == "https://example.com/prices?symbol=7203.T"
        assert request.headers["Authorization"] == "Bearer secret-token"
        return _FakeHttpResponse(payload)

    monkeypatch.setattr("alphalens_experiments.data_adapters.urlopen", fake_urlopen)

    loaded = ApiPriceAdapter(
        provider_name="httpcsv",
        symbols=("7203.T",),
        api_url="https://example.com/prices?symbol={symbol}",
        auth_token="secret-token",
    ).load_prices()

    assert loaded.columns.tolist() == ["7203.T"]
    assert list(loaded.index.strftime("%Y-%m-%d")) == ["2025-01-01", "2025-01-02"]


def test_api_adapter_httpcsv_requires_auth_token() -> None:
    with pytest.raises(ValueError, match="provider=httpcsv requires auth token"):
        ApiPriceAdapter(
            provider_name="httpcsv",
            symbols=("7203.T",),
            api_url="https://example.com/prices?symbol={symbol}",
            auth_token=None,
        ).load_prices()


def test_database_adapter_sqlite_loads_long_format(tmp_path: Path) -> None:
    db_path = tmp_path / "prices.db"
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("CREATE TABLE prices (date TEXT, asset TEXT, close REAL)")
        connection.execute("INSERT INTO prices VALUES ('2025-01-01', '7203.T', 100.0)")
        connection.execute("INSERT INTO prices VALUES ('2025-01-01', '6758.T', 200.0)")
        connection.execute("INSERT INTO prices VALUES ('2025-01-02', '7203.T', 101.0)")
        connection.execute("INSERT INTO prices VALUES ('2025-01-02', '6758.T', 201.0)")
        connection.commit()
    finally:
        connection.close()

    loaded = DatabasePriceAdapter(
        dsn=f"sqlite:///{db_path}", query="SELECT date, asset, close FROM prices"
    ).load_prices()

    assert loaded.columns.tolist() == ["6758.T", "7203.T"]
    assert list(loaded.index.strftime("%Y-%m-%d")) == ["2025-01-01", "2025-01-02"]


def test_build_adapter_requires_parameters() -> None:
    with pytest.raises(ValueError, match="source=csv requires --path"):
        build_adapter(source="csv")

    with pytest.raises(ValueError, match="source=api requires --symbols"):
        build_adapter(source="api", provider="stooq")

    with pytest.raises(ValueError, match="provider=httpcsv requires --api-url"):
        build_adapter(source="api", provider="httpcsv", symbols=("7203.T",)).load_prices()
