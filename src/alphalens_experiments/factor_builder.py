from __future__ import annotations

import numpy as np
import pandas as pd


def make_simple_momentum_factor(prices: pd.DataFrame, lookback: int = 5) -> pd.Series:
    """
    Build a simple cross-sectional momentum factor for Japanese equities.

    factor_t = close_t / close_{t-lookback} - 1
    """
    if lookback <= 0:
        raise ValueError("lookback must be positive")

    momentum = prices / prices.shift(lookback) - 1.0
    factor = momentum.stack().rename("factor").dropna()
    factor.index = factor.index.set_names(["date", "asset"])
    return factor.sort_index()


def make_randomized_factor_like_prices(
    prices: pd.DataFrame, seed: int = 42, scale: float = 0.01
) -> pd.Series:
    """Convenience helper to generate dummy factor values from price shape."""
    rng = np.random.default_rng(seed)
    values = rng.normal(loc=0.0, scale=scale, size=prices.shape)
    factor = (
        pd.DataFrame(values, index=prices.index, columns=prices.columns).stack().rename("factor")
    )
    factor.index = factor.index.set_names(["date", "asset"])
    return factor.sort_index()
