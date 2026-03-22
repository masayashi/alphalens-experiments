from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_run_real_data_pipeline_with_csv_source(tmp_path: Path) -> None:
    raw_csv = tmp_path / "raw_prices.csv"
    processed_dir = tmp_path / "processed"
    reports_dir = tmp_path / "reports"

    dates = pd.bdate_range("2025-01-01", periods=30)
    rows: list[dict[str, object]] = []
    for i, date in enumerate(dates):
        rows.append({"date": date.strftime("%Y-%m-%d"), "asset": "7203.T", "close": 1000.0 + i})
        rows.append({"date": date.strftime("%Y-%m-%d"), "asset": "6758.T", "close": 2000.0 + i})
    pd.DataFrame(rows).to_csv(raw_csv, index=False)

    run_pipeline = subprocess.run(
        [
            sys.executable,
            "scripts/run_real_data_pipeline.py",
            "--source",
            "csv",
            "--path",
            str(raw_csv),
            "--raw-out",
            str(tmp_path / "adapter_loaded_prices.csv"),
            "--processed-dir",
            str(processed_dir),
            "--analysis-summary-out",
            str(reports_dir / "analysis_summary.csv"),
            "--factor-summary-out",
            str(reports_dir / "multi_factor_summary.csv"),
            "--factor-chart-out",
            str(reports_dir / "multi_factor_summary.png"),
            "--skip-tearsheet",
            "--max-loss",
            "0.9",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert run_pipeline.returncode == 0, run_pipeline.stderr
    assert (processed_dir / "prepared_prices_jp.parquet").exists()
    assert (processed_dir / "prepared_factor_jp.parquet").exists()
    assert (reports_dir / "analysis_summary.csv").exists()
    assert (reports_dir / "multi_factor_summary.csv").exists()
    assert (reports_dir / "multi_factor_summary.png").exists()
