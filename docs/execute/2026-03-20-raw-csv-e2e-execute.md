# 実行: 実データ入力向け E2E 拡張（Raw CSV 導線）

## 入力

- 計画参照: `docs/plans/2026-03-20-raw-csv-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. Raw CSV から processed parquet を生成する `scripts/prepare_raw_prices_csv.py` を追加した。
2. `load_prices` を CSV/parquet 両対応に拡張した。
3. Raw CSV 変換から `run_analysis` 実行までの E2E テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check`、`mypy`、`pytest` を全通過した
  - `tests/test_raw_csv_e2e.py` により Raw CSV -> 変換 -> Alphalens 実行の導線を固定した
  - `tests/test_data_loader.py` に CSV 読み込みの回帰テストを追加した
- 意図的に後回しにしたこと:
  - 外部 API / DB 連携
  - 実売買コストやセクター中立化を含む分析高度化
