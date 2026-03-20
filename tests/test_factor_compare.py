from __future__ import annotations

import numpy as np
import pandas as pd

from alphalens_experiments.factor_builder import (
    make_randomized_factor_like_prices,
    make_simple_momentum_factor,
)
from alphalens_experiments.factor_compare import compare_factors


def test_compare_factors_returns_ranked_summary() -> None:
    dates = pd.bdate_range("2025-01-01", periods=80)
    tickers = ["7203.T", "6758.T", "9432.T"]

    rng = np.random.default_rng(7)
    returns = rng.normal(loc=0.0002, scale=0.01, size=(len(dates), len(tickers)))
    prices = pd.DataFrame(1000.0 * (1.0 + returns).cumprod(axis=0), index=dates, columns=tickers)

    factors = {
        "momentum_5": make_simple_momentum_factor(prices=prices, lookback=5),
        "random_baseline": make_randomized_factor_like_prices(prices=prices, seed=42),
    }

    summary = compare_factors(factors=factors, prices=prices, periods=(1, 5), max_loss=0.9)

    assert summary.shape[0] == 2
    assert set(summary["factor"].tolist()) == {"momentum_5", "random_baseline"}
    assert "mean_abs_ic" in summary.columns
    assert (summary["n_obs"] > 0).all()
    assert summary["mean_abs_ic"].notna().all()
