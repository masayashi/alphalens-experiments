import pandas as pd

from alphalens_experiments.factor_builder import make_simple_momentum_factor


def test_make_simple_momentum_factor_shape_and_index_names() -> None:
    dates = pd.bdate_range("2025-01-01", periods=10)
    prices = pd.DataFrame(
        {
            "7203.T": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            "6758.T": [200, 199, 201, 202, 205, 206, 207, 209, 210, 212],
        },
        index=dates,
    )

    factor = make_simple_momentum_factor(prices, lookback=3)

    assert isinstance(factor.index, pd.MultiIndex)
    assert factor.index.names == ["date", "asset"]
    assert len(factor) > 0
    assert factor.notna().all()
