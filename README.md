# alphalens-experiments

日本株のファクター分析を `alphalens`（`alphalens-reloaded`）で行うためのスキャフォールドです。

## 目的

- 対象市場: 日本株（JPX、ティッカー形式は `7203.T` など）
- ゴール: サンプルデータから Alphalens の tear sheet を end-to-end で実行できる状態にする
- リポジトリ中心で再現可能な依存管理を行う

## プロジェクト構成

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

## セットアップ（推奨: uv + .venv）

1. `uv` をインストール（初回のみ）

```powershell
python -m pip install --upgrade uv
```

2. 仮想環境作成と依存同期

```powershell
uv venv .venv
uv sync --extra dev
```

3. `uv run` 経由で実行

```powershell
uv run pytest -q
```

4. pre-commit フックを有効化

```powershell
uv run pre-commit install
```

5. Windows 権限エラー回避のローカル設定（推奨）

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_local_harness.ps1
```

## クイックスタート

1. 日本株サンプルデータ生成

```powershell
uv run python scripts\generate_sample_jp_data.py
```

2. Alphalens 分析実行

```powershell
uv run python -m alphalens_experiments.run_analysis `
  --prices data\processed\sample_prices_jp.parquet `
  --factor data\processed\sample_factor_jp.parquet `
  --periods 1 5 10
```

実行ログは `reports/tearsheet_output.txt`、要約は `reports/analysis_summary.csv` に出力されます（IC、分位リターン、上位-下位スプレッド、スプレッドt値、年率換算を含む）。

## 実データパイプライン

- CSV 入力（long/wide）から一気通貫で実行:

```powershell
uv run python scripts\run_real_data_pipeline.py `
  --source csv `
  --path data\raw\your_prices.csv `
  --skip-tearsheet
```

- API 入力（`stooq`）の例:

```powershell
uv run python scripts\run_real_data_pipeline.py `
  --source api `
  --provider stooq `
  --symbols 7203.T,6758.T,9432.T `
  --start 2024-01-01 `
  --end 2025-12-31 `
  --skip-tearsheet
```\n\nトークン設定例（PowerShell）:\n\n```powershell\n$env:ALPHALENS_API_TOKEN = "<YOUR_TOKEN>"\n```\n\n- 祝日CSVをURLから自動取得（公式URLは運用側で指定）:

```powershell
uv run python scripts\fetch_jpx_holidays_csv.py `
  --url "https://example.com/jpx-holidays.csv" `
  --out configs\jpx_holidays_latest.csv
```

- 一気通貫パイプラインで祝日CSVを自動取得して利用:

```powershell
uv run python scripts\run_real_data_pipeline.py `
  --source csv `
  --path data\raw\your_prices.csv `
  --jpx-holidays-url "https://example.com/jpx-holidays.csv" `
  --jpx-holidays-out configs\jpx_holidays_latest.csv `
  --skip-tearsheet
```

出力物:
- `data/raw/adapter_loaded_prices.csv`
- `data/processed/prepared_prices_jp.parquet`
- `data/processed/prepared_factor_jp.parquet`
- `reports/analysis_summary.csv`
- `reports/multi_factor_summary.csv`
- `reports/multi_factor_summary.png`

## データ仕様

- `prices`:
  - index: `DatetimeIndex`
  - columns: 銘柄ティッカー（例: `7203.T`）
  - values: 終値（`float`）
- `factor`:
  - index: `MultiIndex(date, asset)`
  - values: ファクタースコア（`float`）

## 補足

- `uv.lock` は再現可能な環境構築のために生成されます。
- サードパーティライブラリ由来の警告が出る場合がありますが、現時点の実行は成功しています。

## ハーネス（Week 1 基盤）

- エージェント向けポインタ: `AGENTS.md`
- ADR: `docs/adr/ADR-0001-harness-policy.md`
- 計画/実行テンプレート:
  - `docs/templates/PLAN.md`
  - `docs/templates/EXECUTE.md`
- 決定論的な実行ループ:
  1. `uv run ruff format .`
  2. `uv run ruff check .`
  3. `uv run mypy`
  4. `uv run pytest -q`
- Stop 条件:
  - `ruff check` / `mypy` / `pytest` がすべて成功していること。

## 権限エラー対策

このリポジトリでは、以下のキャッシュをリポジトリ内に固定することで、
`AppData` 配下へのアクセス権限問題を回避します。

- `UV_CACHE_DIR=.uv-cache`
- `PRE_COMMIT_HOME=.pre-commit-cache`
- `VIRTUALENV_OVERRIDE_APP_DATA=.virtualenv-cache`

一括実行コマンド:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_quality_gate.ps1
```

- APIトークン運用方針: `docs/specs/api-token-operation-policy.md`



