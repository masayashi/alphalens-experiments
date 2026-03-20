from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot factor summary CSV as bar chart.")
    parser.add_argument("--summary", required=True, help="Path to multi-factor summary CSV.")
    parser.add_argument(
        "--out", default="reports/multi_factor_summary.png", help="Output PNG path."
    )
    parser.add_argument("--metric", default="mean_abs_ic", help="Metric column to visualize.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary_path = Path(args.summary)
    out_path = Path(args.out)

    frame = pd.read_csv(summary_path)
    if "factor" not in frame.columns:
        raise ValueError("summary csv must contain 'factor' column")
    if args.metric not in frame.columns:
        raise ValueError(f"summary csv must contain '{args.metric}' column")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(frame["factor"], frame[args.metric], color="#1f77b4")
    ax.set_title(f"Factor Comparison ({args.metric})")
    ax.set_xlabel("factor")
    ax.set_ylabel(args.metric)
    ax.tick_params(axis="x", labelrotation=20)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"Saved chart: {out_path}")


if __name__ == "__main__":
    main()
