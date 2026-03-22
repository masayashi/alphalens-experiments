from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from alphalens_experiments.calendar_policy import apply_jp_price_policy, load_holidays_csv
from alphalens_experiments.factor_builder import make_simple_momentum_factor
from alphalens_experiments.holiday_fetcher import fetch_holidays_csv


def _load_raw_prices(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    lowered = {column.lower(): column for column in frame.columns}

    if {"date", "asset", "close"}.issubset(lowered):
        date_col = lowered["date"]
        asset_col = lowered["asset"]
        close_col = lowered["close"]
        prices = (
            frame.assign(
                date=lambda x: pd.to_datetime(x[date_col]), asset=lambda x: x[asset_col].astype(str)
            )
            .pivot(index="date", columns="asset", values=close_col)
            .sort_index()
        )
        return prices

    if "date" in lowered:
        date_col = lowered["date"]
        prices = frame.rename(columns={date_col: "date"}).set_index("date")
        prices.index = pd.to_datetime(prices.index)
        prices.columns = prices.columns.astype(str)
        return prices.sort_index()

    raise ValueError("raw prices csv must be long(date,asset,close) or wide(date + ticker columns)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare processed prices/factor parquet from raw CSV."
    )
    parser.add_argument("--raw-prices", required=True, help="Path to raw prices csv.")
    parser.add_argument(
        "--out-dir", default="data/processed", help="Output directory for generated parquet files."
    )
    parser.add_argument(
        "--lookback", type=int, default=5, help="Lookback days for momentum factor."
    )
    parser.add_argument(
        "--jpx-holidays-csv",
        help="Optional CSV containing JP holiday dates in `date` column.",
    )
    parser.add_argument(
        "--jpx-holidays-url",
        help="Optional URL to fetch JP holiday CSV automatically.",
    )
    parser.add_argument(
        "--jpx-holidays-out",
        default="configs/jpx_holidays_latest.csv",
        help="Destination path when --jpx-holidays-url is used.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_prices_path = Path(args.raw_prices)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.jpx_holidays_csv and args.jpx_holidays_url:
        raise ValueError("--jpx-holidays-csv and --jpx-holidays-url are mutually exclusive")

    holidays_csv_path: str | None = args.jpx_holidays_csv
    if args.jpx_holidays_url:
        fetched = fetch_holidays_csv(args.jpx_holidays_url, args.jpx_holidays_out)
        holidays_csv_path = str(fetched)

    raw_prices = _load_raw_prices(raw_prices_path)
    holidays = load_holidays_csv(holidays_csv_path) if holidays_csv_path else set()
    prices = apply_jp_price_policy(raw_prices, holidays=holidays)
    factor = make_simple_momentum_factor(prices=prices, lookback=args.lookback)

    prices_path = out_dir / "prepared_prices_jp.parquet"
    factor_path = out_dir / "prepared_factor_jp.parquet"

    prices.to_parquet(prices_path)
    factor.to_frame(name="factor").to_parquet(factor_path)

    print(f"Saved prices: {prices_path}")
    print(f"Saved factor: {factor_path}")


if __name__ == "__main__":
    main()
