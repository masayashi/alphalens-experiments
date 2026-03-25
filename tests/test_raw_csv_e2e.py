from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_raw_csv_to_analysis_e2e(tmp_path: Path) -> None:
    raw_prices_path = tmp_path / "raw_prices.csv"
    out_dir = tmp_path / "processed"
    summary_path = tmp_path / "analysis_summary.csv"

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
            "--summary-out",
            str(summary_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_analysis.returncode == 0, run_analysis.stderr

    log_path = Path("reports/tearsheet_output.txt")
    assert log_path.exists()
    assert "Rows in factor_data:" in log_path.read_text(encoding="utf-8")
    assert summary_path.exists()

    summary = pd.read_csv(summary_path)
    assert "top_quantile" in summary.columns
    assert "bottom_quantile" in summary.columns
    assert "mean_ret_spread_q5_q1_1D" in summary.columns
    assert "tstat_ret_spread_q5_q1_1D" in summary.columns
    assert "ann_ret_spread_q5_q1_1D" in summary.columns


def test_prepare_script_applies_weekday_and_missing_policy(tmp_path: Path) -> None:
    raw_prices_path = tmp_path / "raw_prices_with_gap.csv"
    out_dir = tmp_path / "processed"

    rows = [
        {"date": "2025-01-03", "asset": "7203.T", "close": 1000.0},
        {"date": "2025-01-03", "asset": "6758.T", "close": 2000.0},
        {"date": "2025-01-04", "asset": "7203.T", "close": 1001.0},
        {"date": "2025-01-04", "asset": "6758.T", "close": 2001.0},
        {"date": "2025-01-06", "asset": "7203.T", "close": 1002.0},
    ]
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
            "1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_prepare.returncode == 0, run_prepare.stderr

    prices = pd.read_parquet(out_dir / "prepared_prices_jp.parquet")

    assert list(prices.index.strftime("%Y-%m-%d")) == ["2025-01-03"]


def test_prepare_script_applies_holiday_csv(tmp_path: Path) -> None:
    raw_prices_path = tmp_path / "raw_prices_holiday.csv"
    holiday_csv_path = tmp_path / "holidays.csv"
    out_dir = tmp_path / "processed"

    rows = [
        {"date": "2025-01-03", "asset": "7203.T", "close": 1000.0},
        {"date": "2025-01-03", "asset": "6758.T", "close": 2000.0},
        {"date": "2025-01-06", "asset": "7203.T", "close": 1001.0},
        {"date": "2025-01-06", "asset": "6758.T", "close": 2001.0},
        {"date": "2025-01-07", "asset": "7203.T", "close": 1002.0},
        {"date": "2025-01-07", "asset": "6758.T", "close": 2002.0},
    ]
    pd.DataFrame(rows).to_csv(raw_prices_path, index=False)
    pd.DataFrame({"date": ["2025-01-06"]}).to_csv(holiday_csv_path, index=False)

    run_prepare = subprocess.run(
        [
            sys.executable,
            "scripts/prepare_raw_prices_csv.py",
            "--raw-prices",
            str(raw_prices_path),
            "--out-dir",
            str(out_dir),
            "--lookback",
            "1",
            "--jpx-holidays-csv",
            str(holiday_csv_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_prepare.returncode == 0, run_prepare.stderr

    prices = pd.read_parquet(out_dir / "prepared_prices_jp.parquet")

    assert list(prices.index.strftime("%Y-%m-%d")) == ["2025-01-03", "2025-01-07"]


def test_prepare_script_rejects_conflicting_holiday_options(tmp_path: Path) -> None:
    raw_prices_path = tmp_path / "raw_prices.csv"
    out_dir = tmp_path / "processed"
    holiday_csv_path = tmp_path / "holidays.csv"

    pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-01-02"],
            "7203.T": [100.0, 101.0],
            "6758.T": [200.0, 201.0],
        }
    ).to_csv(raw_prices_path, index=False)
    pd.DataFrame({"date": ["2025-01-01"]}).to_csv(holiday_csv_path, index=False)

    run_prepare = subprocess.run(
        [
            sys.executable,
            "scripts/prepare_raw_prices_csv.py",
            "--raw-prices",
            str(raw_prices_path),
            "--out-dir",
            str(out_dir),
            "--jpx-holidays-csv",
            str(holiday_csv_path),
            "--jpx-holidays-url",
            "https://example.com/holidays.csv",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert run_prepare.returncode != 0
    assert "mutually exclusive" in run_prepare.stderr
