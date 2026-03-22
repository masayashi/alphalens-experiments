from __future__ import annotations

import argparse
from pathlib import Path

import alphalens as al
import matplotlib
import pandas as pd

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from alphalens_experiments.calendar_policy import apply_jp_price_policy, load_holidays_csv
from alphalens_experiments.data_adapters import CsvPriceAdapter, build_adapter, save_loaded_prices
from alphalens_experiments.factor_builder import (
    make_randomized_factor_like_prices,
    make_simple_momentum_factor,
)
from alphalens_experiments.factor_compare import compare_factors
from alphalens_experiments.run_analysis import build_analysis_summary, run_alphalens_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run real-data pipeline: fetch -> prepare -> analysis -> compare -> plot"
    )
    parser.add_argument("--source", choices=["csv", "api", "db"], required=True)
    parser.add_argument("--path", help="Input path for source=csv")
    parser.add_argument("--provider", help="Provider name for source=api")
    parser.add_argument("--symbols", help="Comma-separated symbols for source=api")
    parser.add_argument("--start", help="Start date for source=api")
    parser.add_argument("--end", help="End date for source=api")
    parser.add_argument("--dsn", help="DSN for source=db")
    parser.add_argument("--query", help="Query for source=db")
    parser.add_argument("--raw-out", default="data/raw/adapter_loaded_prices.csv")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--lookback", type=int, default=5)
    parser.add_argument("--jpx-holidays-csv", help="Optional JP holiday CSV path")
    parser.add_argument("--periods", nargs="+", type=int, default=[1, 5, 10])
    parser.add_argument("--max-loss", type=float, default=0.35)
    parser.add_argument("--analysis-summary-out", default="reports/analysis_summary.csv")
    parser.add_argument("--factor-summary-out", default="reports/multi_factor_summary.csv")
    parser.add_argument("--factor-chart-out", default="reports/multi_factor_summary.png")
    parser.add_argument("--skip-tearsheet", action="store_true")
    return parser.parse_args()


def _parse_symbols(raw: str | None) -> tuple[str, ...]:
    if raw is None:
        return ()
    return tuple(symbol.strip() for symbol in raw.split(",") if symbol.strip())


def _save_factor_chart(summary: pd.DataFrame, out_path: Path, metric: str = "mean_abs_ic") -> None:
    if metric not in summary.columns:
        raise ValueError(f"summary must contain '{metric}' column")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(summary["factor"], summary[metric], color="#1f77b4")
    ax.set_title(f"Factor Comparison ({metric})")
    ax.set_xlabel("factor")
    ax.set_ylabel(metric)
    ax.tick_params(axis="x", labelrotation=20)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    args = parse_args()

    adapter = build_adapter(
        source=args.source,
        path=args.path,
        provider=args.provider,
        symbols=_parse_symbols(args.symbols),
        start=args.start,
        end=args.end,
        dsn=args.dsn,
        query=args.query,
    )
    loaded_prices = adapter.load_prices()
    raw_out = save_loaded_prices(loaded_prices, args.raw_out)

    raw_prices = CsvPriceAdapter(path=str(raw_out)).load_prices()
    holidays = load_holidays_csv(args.jpx_holidays_csv) if args.jpx_holidays_csv else set()
    prepared_prices = apply_jp_price_policy(raw_prices, holidays=holidays)
    prepared_factor = make_simple_momentum_factor(prices=prepared_prices, lookback=args.lookback)

    processed_dir = Path(args.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    prices_path = processed_dir / "prepared_prices_jp.parquet"
    factor_path = processed_dir / "prepared_factor_jp.parquet"
    prepared_prices.to_parquet(prices_path)
    prepared_factor.to_frame(name="factor").to_parquet(factor_path)

    factor_data = run_alphalens_analysis(
        prices=prepared_prices,
        factor=prepared_factor,
        periods=tuple(args.periods),
        max_loss=args.max_loss,
    )
    analysis_summary = build_analysis_summary(factor_data)
    analysis_summary_out = Path(args.analysis_summary_out)
    analysis_summary_out.parent.mkdir(parents=True, exist_ok=True)
    analysis_summary.to_csv(analysis_summary_out, index=False)

    if not args.skip_tearsheet:
        al.tears.create_full_tear_sheet(factor_data)

    factors = {
        f"momentum_{args.lookback}": prepared_factor,
        "random_baseline": make_randomized_factor_like_prices(prices=prepared_prices, seed=42),
    }
    factor_summary = compare_factors(
        factors=factors,
        prices=prepared_prices,
        periods=tuple(args.periods),
        max_loss=max(args.max_loss, 0.7),
    )
    factor_summary_out = Path(args.factor_summary_out)
    factor_summary_out.parent.mkdir(parents=True, exist_ok=True)
    factor_summary.to_csv(factor_summary_out, index=False)

    _save_factor_chart(factor_summary, Path(args.factor_chart_out))

    print(f"Saved raw prices: {raw_out}")
    print(f"Saved prepared prices: {prices_path}")
    print(f"Saved prepared factor: {factor_path}")
    print(f"Saved analysis summary: {analysis_summary_out}")
    print(f"Saved factor summary: {factor_summary_out}")
    print(f"Saved factor chart: {args.factor_chart_out}")


if __name__ == "__main__":
    main()
