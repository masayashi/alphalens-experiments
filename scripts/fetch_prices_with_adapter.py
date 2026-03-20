from __future__ import annotations

import argparse

from alphalens_experiments.data_adapters import build_adapter, save_loaded_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load prices via adapter and save as raw CSV.")
    parser.add_argument("--source", choices=["csv", "api", "db"], required=True)
    parser.add_argument("--path", help="Input path for source=csv")
    parser.add_argument("--provider", help="Provider name for source=api")
    parser.add_argument("--dsn", help="DSN for source=db")
    parser.add_argument("--query", help="Query for source=db")
    parser.add_argument("--out", default="data/raw/adapter_loaded_prices.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    adapter = build_adapter(
        source=args.source,
        path=args.path,
        provider=args.provider,
        dsn=args.dsn,
        query=args.query,
    )
    prices = adapter.load_prices()
    saved = save_loaded_prices(prices=prices, out_path=args.out)
    print(f"Saved prices: {saved}")


if __name__ == "__main__":
    main()
