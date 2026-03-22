from __future__ import annotations

import argparse
import sys

from alphalens_experiments.data_adapters import build_adapter, save_loaded_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load prices via adapter and save as raw CSV.")
    parser.add_argument("--source", choices=["csv", "api", "db"], required=True)
    parser.add_argument("--path", help="Input path for source=csv")
    parser.add_argument("--provider", help="Provider name for source=api (e.g., stooq)")
    parser.add_argument("--symbols", help="Comma-separated symbols for source=api")
    parser.add_argument("--start", help="Start date for source=api (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date for source=api (YYYY-MM-DD)")
    parser.add_argument("--dsn", help="DSN for source=db (e.g., sqlite:///data/raw/prices.db)")
    parser.add_argument("--query", help="Query for source=db")
    parser.add_argument("--out", default="data/raw/adapter_loaded_prices.csv")
    return parser.parse_args()


def _parse_symbols(raw: str | None) -> tuple[str, ...]:
    if raw is None:
        return ()
    symbols = tuple(symbol.strip() for symbol in raw.split(",") if symbol.strip())
    return symbols


def main() -> None:
    args = parse_args()

    try:
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
        prices = adapter.load_prices()
        saved = save_loaded_prices(prices=prices, out_path=args.out)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to load prices: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Saved prices: {saved}")


if __name__ == "__main__":
    main()
