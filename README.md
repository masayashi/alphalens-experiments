# alphalens-experiments

Scaffold for JP equity factor analysis with `alphalens` (`alphalens-reloaded`).

## Scope

- Target market: Japanese equities (JPX, ticker format like `7203.T`)
- Goal: run an end-to-end Alphalens tear sheet from sample data
- Repo-first setup with reproducible dependency management

## Project layout

```text
.
|- configs/
|- data/
|  |- raw/
|  `- processed/
|- notebooks/
|- reports/
|- scripts/
|- src/
|  `- alphalens_experiments/
|     |- __init__.py
|     |- data_loader.py
|     |- factor_builder.py
|     `- run_analysis.py
`- tests/
```

## Setup (recommended: uv + .venv)

1. Install `uv` (one-time):

```powershell
python -m pip install --upgrade uv
```

2. Create venv and sync dependencies:

```powershell
uv venv .venv
uv sync --extra dev
```

3. Run commands through `uv run`:

```powershell
uv run pytest -q
```

## Quick start

1. Generate sample JP data:

```powershell
uv run python scripts\generate_sample_jp_data.py
```

2. Run Alphalens analysis:

```powershell
uv run python -m alphalens_experiments.run_analysis `
  --prices data\processed\sample_prices_jp.parquet `
  --factor data\processed\sample_factor_jp.parquet `
  --periods 1 5 10
```

Execution log is written to `reports/tearsheet_output.txt`.

## Data contract

- `prices`:
  - index: `DatetimeIndex`
  - columns: asset ticker (example: `7203.T`)
  - values: close price (`float`)
- `factor`:
  - index: `MultiIndex(date, asset)`
  - values: factor score (`float`)

## Notes

- `uv.lock` is generated for reproducible environments.
- Some warnings may come from third-party libs; current run is successful.
