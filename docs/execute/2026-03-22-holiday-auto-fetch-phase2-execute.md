# 実行: JPX祝日CSVの自動取得ジョブ追加（Phase 2）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `holiday_fetcher.py` を追加し、URL取得 -> 日付列正規化 -> `date` 1列CSV保存を実装した。
2. `fetch_jpx_holidays_csv.py` を追加し、祝日CSVをURLから取得するCLIを追加した。
3. `prepare_raw_prices_csv.py` と `run_real_data_pipeline.py` に `--jpx-holidays-url/--jpx-holidays-out` を追加した。
4. `--jpx-holidays-csv` と `--jpx-holidays-url` の排他制約を導入した。
5. 祝日自動取得のテストを追加し、CLI排他制約の回帰を固定した。
6. README とカレンダー仕様書を v3 として更新した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`
- `$env:UV_CACHE_DIR='.uv-cache'; uv run pytest -q tests/test_holiday_fetcher.py tests/test_real_data_pipeline.py`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - JPX祝日CSVのURL自動取得ジョブを追加した
  - 実データパイプラインから祝日自動取得を直接呼べるようにした
  - 祝日列名ゆれ（`date/Date/日付/年月日`）を正規化して取り込めるようにした
- 意図的に後回しにしたこと:
  - 公式ソースURLの固定と署名/ハッシュ検証
  - 祝日データ取得の定期実行（automation）設定
