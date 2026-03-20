from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from alphalens_experiments.factor_builder import make_simple_momentum_factor


def make_price_paths(
    dates: pd.DatetimeIndex, tickers: list[str], seed: int = 7, start_price: float = 1000.0
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_dates = len(dates)
    n_assets = len(tickers)

    daily_ret = rng.normal(loc=0.0002, scale=0.015, size=(n_dates, n_assets))
    prices = np.zeros((n_dates, n_assets))
    prices[0, :] = start_price

    for i in range(1, n_dates):
        prices[i, :] = prices[i - 1, :] * (1.0 + daily_ret[i, :])

    return pd.DataFrame(prices, index=dates, columns=tickers)


def main() -> None:
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    dates = pd.bdate_range("2024-01-01", "2025-12-31")
    # Representative JP tickers in TSE notation.
    tickers = ["7203.T", "6758.T", "9984.T", "8306.T", "9432.T", "7974.T"]

    prices = make_price_paths(dates=dates, tickers=tickers)
    factor = make_simple_momentum_factor(prices=prices, lookback=5)

    prices_path = output_dir / "sample_prices_jp.parquet"
    factor_path = output_dir / "sample_factor_jp.parquet"

    prices.to_parquet(prices_path)
    factor.to_frame(name="factor").to_parquet(factor_path)

    print(f"Saved prices: {prices_path}")
    print(f"Saved factor: {factor_path}")


if __name__ == "__main__":
    main()

