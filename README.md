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

実行ログは `reports/tearsheet_output.txt` に出力されます。

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
  3. `uv run pytest -q`
