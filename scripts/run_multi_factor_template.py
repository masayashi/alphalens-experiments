from __future__ import annotations

import argparse
from pathlib import Path

from alphalens_experiments.data_loader import load_prices
from alphalens_experiments.factor_builder import (
    make_randomized_factor_like_prices,
    make_simple_momentum_factor,
)
from alphalens_experiments.factor_compare import compare_factors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multi-factor comparison template.")
    parser.add_argument("--prices", required=True, help="Path to prices parquet/csv.")
    parser.add_argument(
        "--out",
        default="reports/multi_factor_summary.csv",
        help="Output CSV path for factor comparison summary.",
    )
    parser.add_argument("--periods", nargs="+", type=int, default=[1, 5, 10])
    parser.add_argument("--lookback", type=int, default=5)
    parser.add_argument("--max-loss", type=float, default=0.7)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    prices = load_prices(args.prices)
    factors = {
        f"momentum_{args.lookback}": make_simple_momentum_factor(
            prices=prices, lookback=args.lookback
        ),
        "random_baseline": make_randomized_factor_like_prices(prices=prices, seed=args.seed),
    }

    summary = compare_factors(
        factors=factors,
        prices=prices,
        periods=tuple(args.periods),
        max_loss=args.max_loss,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_path, index=False)

    print(f"Saved factor summary: {out_path}")


if __name__ == "__main__":
    main()
