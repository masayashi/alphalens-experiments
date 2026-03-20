from __future__ import annotations

from collections.abc import Mapping

import alphalens as al
import pandas as pd


def compare_factors(
    factors: Mapping[str, pd.Series],
    prices: pd.DataFrame,
    periods: tuple[int, ...] = (1, 5, 10),
    max_loss: float = 0.35,
) -> pd.DataFrame:
    """Compare multiple factors with a compact IC-based summary."""
    records: list[dict[str, float | int | str]] = []

    for factor_name, factor_values in factors.items():
        factor_data = al.utils.get_clean_factor_and_forward_returns(
            factor=factor_values,
            prices=prices,
            periods=periods,
            max_loss=max_loss,
        )
        ic = al.performance.factor_information_coefficient(factor_data)

        record: dict[str, float | int | str] = {
            "factor": factor_name,
            "n_obs": int(len(factor_data)),
            "mean_ic": float(ic.mean().mean()),
            "mean_abs_ic": float(ic.abs().mean().mean()),
        }
        for column in ic.columns:
            record[f"ic_{column}"] = float(ic[column].mean())
        records.append(record)

    result = pd.DataFrame(records)
    return result.sort_values("mean_abs_ic", ascending=False).reset_index(drop=True)
