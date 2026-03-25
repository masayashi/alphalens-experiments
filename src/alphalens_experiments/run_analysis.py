from __future__ import annotations

import argparse
from pathlib import Path
import re

import alphalens as al
import numpy as np
import pandas as pd

from .data_loader import load_factor, load_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Alphalens analysis for Japanese equities.")
    parser.add_argument("--prices", required=True, help="Path to price parquet/csv.")
    parser.add_argument("--factor", required=True, help="Path to factor parquet.")
    parser.add_argument(
        "--periods", nargs="+", type=int, default=[1, 5, 10], help="Forward periods."
    )
    parser.add_argument(
        "--max-loss",
        type=float,
        default=0.35,
        help="Max data loss threshold in get_clean_factor_and_forward_returns.",
    )
    parser.add_argument(
        "--summary-out",
        default="reports/analysis_summary.csv",
        help="Output CSV path for analysis summary.",
    )
    parser.add_argument(
        "--skip-tearsheet",
        action="store_true",
        help="Skip chart rendering and only produce cleaned factor data stats.",
    )
    return parser.parse_args()


def _forward_return_columns(factor_data: pd.DataFrame) -> list[object]:
    excluded = {"factor", "factor_quantile", "group"}
    return [column for column in factor_data.columns if str(column) not in excluded]


def _extract_period_days(column_name: str) -> int:
    match = re.search(r"(\d+)", column_name)
    if match is None:
        return 1
    return max(1, int(match.group(1)))


def _safe_t_stat(series: pd.Series) -> float:
    cleaned = series.dropna()
    n = len(cleaned)
    if n < 2:
        return 0.0
    std = float(cleaned.std(ddof=1))
    if std == 0.0:
        return 0.0
    mean = float(cleaned.mean())
    return mean / (std / np.sqrt(n))


def build_analysis_summary(factor_data: pd.DataFrame) -> pd.DataFrame:
    ic = al.performance.factor_information_coefficient(factor_data)
    forward_cols = _forward_return_columns(factor_data)

    summary: dict[str, float | int | str] = {
        "n_rows": int(len(factor_data)),
        "n_assets": int(factor_data.index.get_level_values("asset").nunique()),
        "start_date": str(factor_data.index.get_level_values("date").min().date()),
        "end_date": str(factor_data.index.get_level_values("date").max().date()),
        "mean_factor": float(factor_data["factor"].mean()),
        "std_factor": float(factor_data["factor"].std()),
    }

    for column in ic.columns:
        summary[f"mean_ic_{column}"] = float(ic[column].mean())

    quantile_means = factor_data.groupby("factor_quantile")[forward_cols].mean()
    top_quantile = int(quantile_means.index.max())
    bottom_quantile = int(quantile_means.index.min())

    summary["top_quantile"] = top_quantile
    summary["bottom_quantile"] = bottom_quantile

    for column in forward_cols:
        column_name = str(column)
        top_value = float(quantile_means.loc[top_quantile, column])
        bottom_value = float(quantile_means.loc[bottom_quantile, column])
        spread_value = top_value - bottom_value
        summary[f"mean_ret_q{top_quantile}_{column_name}"] = top_value
        summary[f"mean_ret_q{bottom_quantile}_{column_name}"] = bottom_value
        summary[f"mean_ret_spread_q{top_quantile}_q{bottom_quantile}_{column_name}"] = spread_value

        by_date_quantile = (
            factor_data.reset_index()
            .groupby(["date", "factor_quantile"])[column]
            .mean()
            .unstack("factor_quantile")
        )
        spread_series = by_date_quantile[top_quantile] - by_date_quantile[bottom_quantile]
        summary[f"tstat_ret_spread_q{top_quantile}_q{bottom_quantile}_{column_name}"] = (
            _safe_t_stat(spread_series)
        )
        period_days = _extract_period_days(column_name)
        annualized = spread_value * (252.0 / period_days)
        summary[f"ann_ret_spread_q{top_quantile}_q{bottom_quantile}_{column_name}"] = annualized

    return pd.DataFrame([summary])


def run_alphalens_analysis(
    prices: pd.DataFrame,
    factor: pd.Series,
    periods: tuple[int, ...],
    max_loss: float,
) -> pd.DataFrame:
    return al.utils.get_clean_factor_and_forward_returns(
        factor=factor,
        prices=prices,
        periods=periods,
        max_loss=max_loss,
    )


def main() -> None:
    args = parse_args()
    prices = load_prices(args.prices)
    factor = load_factor(args.factor)

    factor_data = run_alphalens_analysis(
        prices=prices,
        factor=factor,
        periods=tuple(args.periods),
        max_loss=args.max_loss,
    )

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    log_path = reports_dir / "tearsheet_output.txt"

    summary = build_analysis_summary(factor_data)
    summary_out = Path(args.summary_out)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_out, index=False)

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write("Alphalens analysis started.\n")
        log_file.write(f"Rows in factor_data: {len(factor_data)}\n")
        log_file.write(f"Columns: {list(factor_data.columns)}\n")
        log_file.write(f"Summary CSV: {summary_out}\n")

    if not args.skip_tearsheet:
        al.tears.create_full_tear_sheet(factor_data)


if __name__ == "__main__":
    main()
