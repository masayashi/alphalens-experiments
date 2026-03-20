from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_plot_factor_summary_creates_png(tmp_path: Path) -> None:
    summary_csv = tmp_path / "multi_factor_summary.csv"
    output_png = tmp_path / "multi_factor_summary.png"

    pd.DataFrame(
        {
            "factor": ["momentum_5", "random_baseline"],
            "mean_abs_ic": [0.12, 0.03],
        }
    ).to_csv(summary_csv, index=False)

    run_plot = subprocess.run(
        [
            sys.executable,
            "scripts/plot_factor_summary.py",
            "--summary",
            str(summary_csv),
            "--out",
            str(output_png),
            "--metric",
            "mean_abs_ic",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert run_plot.returncode == 0, run_plot.stderr
    assert output_png.exists()
    assert output_png.stat().st_size > 0
