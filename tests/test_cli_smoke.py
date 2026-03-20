from __future__ import annotations

import subprocess
import sys


def test_cli_pipeline_smoke() -> None:
    run_generate = subprocess.run(
        [sys.executable, "scripts/generate_sample_jp_data.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_generate.returncode == 0, run_generate.stderr

    run_analysis = subprocess.run(
        [
            sys.executable,
            "-m",
            "alphalens_experiments.run_analysis",
            "--prices",
            "data/processed/sample_prices_jp.parquet",
            "--factor",
            "data/processed/sample_factor_jp.parquet",
            "--periods",
            "1",
            "5",
            "10",
            "--skip-tearsheet",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_analysis.returncode == 0, run_analysis.stderr
