from __future__ import annotations

import argparse
import sys

from alphalens_experiments.holiday_fetcher import fetch_holidays_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch JP holiday calendar CSV from URL and save as standardized date CSV."
    )
    parser.add_argument("--url", required=True, help="Holiday CSV URL (official source URL)")
    parser.add_argument("--out", default="configs/jpx_holidays_latest.csv")
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        out_path = fetch_holidays_csv(
            source_url=args.url,
            out_path=args.out,
            max_retries=args.max_retries,
            timeout_seconds=args.timeout_seconds,
            encoding=args.encoding,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to fetch holidays: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Saved holidays: {out_path}")


if __name__ == "__main__":
    main()
