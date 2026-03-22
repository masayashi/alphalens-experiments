from __future__ import annotations

import argparse
from pathlib import Path

import alphalens as al
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


def build_analysis_summary(factor_data: pd.DataFrame) -> pd.DataFrame:
    ic = al.performance.factor_information_coefficient(factor_data)
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
