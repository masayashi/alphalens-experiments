from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_raw_csv_to_analysis_e2e(tmp_path: Path) -> None:
    raw_prices_path = tmp_path / "raw_prices.csv"
    out_dir = tmp_path / "processed"

    dates = pd.bdate_range("2025-01-01", periods=30)
    rows: list[dict[str, object]] = []
    for date in dates:
        rows.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "asset": "7203.T",
                "close": 1000.0 + len(rows),
            }
        )
        rows.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "asset": "6758.T",
                "close": 2000.0 + len(rows),
            }
        )

    pd.DataFrame(rows).to_csv(raw_prices_path, index=False)

    run_prepare = subprocess.run(
        [
            sys.executable,
            "scripts/prepare_raw_prices_csv.py",
            "--raw-prices",
            str(raw_prices_path),
            "--out-dir",
            str(out_dir),
            "--lookback",
            "5",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_prepare.returncode == 0, run_prepare.stderr

    prepared_prices = out_dir / "prepared_prices_jp.parquet"
    prepared_factor = out_dir / "prepared_factor_jp.parquet"

    assert prepared_prices.exists()
    assert prepared_factor.exists()

    run_analysis = subprocess.run(
        [
            sys.executable,
            "-m",
            "alphalens_experiments.run_analysis",
            "--prices",
            str(prepared_prices),
            "--factor",
            str(prepared_factor),
            "--periods",
            "1",
            "5",
            "10",
            "--skip-tearsheet",
            "--max-loss",
            "0.7",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_analysis.returncode == 0, run_analysis.stderr

    log_path = Path("reports/tearsheet_output.txt")
    assert log_path.exists()
    assert "Rows in factor_data:" in log_path.read_text(encoding="utf-8")
