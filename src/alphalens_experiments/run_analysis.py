from __future__ import annotations

import argparse
from pathlib import Path

import alphalens as al

from .data_loader import load_factor, load_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Alphalens analysis for Japanese equities.")
    parser.add_argument("--prices", required=True, help="Path to price parquet.")
    parser.add_argument("--factor", required=True, help="Path to factor parquet.")
    parser.add_argument("--periods", nargs="+", type=int, default=[1, 5, 10], help="Forward periods.")
    parser.add_argument(
        "--max-loss",
        type=float,
        default=0.35,
        help="Max data loss threshold in get_clean_factor_and_forward_returns.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prices = load_prices(args.prices)
    factor = load_factor(args.factor)

    factor_data = al.utils.get_clean_factor_and_forward_returns(
        factor=factor,
        prices=prices,
        periods=tuple(args.periods),
        max_loss=args.max_loss,
    )

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    log_path = reports_dir / "tearsheet_output.txt"

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write("Alphalens analysis started.\n")
        log_file.write(f"Rows in factor_data: {len(factor_data)}\n")
        log_file.write(f"Columns: {list(factor_data.columns)}\n")

    al.tears.create_full_tear_sheet(factor_data)


if __name__ == "__main__":
    main()

