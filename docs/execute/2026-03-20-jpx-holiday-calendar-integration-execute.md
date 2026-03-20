# 実行: JPX 祝日カレンダー連携（CSV 注入方式）

## 入力

- 計画参照: `docs/plans/2026-03-20-jpx-holiday-calendar-integration-plan.md`
- ブランチ: `master`

## 変更内容

1. `calendar_policy.py` に祝日CSV読込と祝日除外処理を追加した。
2. `prepare_raw_prices_csv.py` に `--jpx-holidays-csv` オプションを追加した。
3. 祝日除外の単体/E2Eテストを追加した。
4. 仕様書を v2 に更新し、サンプル祝日CSVを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` により `ruff check` / `mypy` / `pytest` の全通過を確認した
  - 平日近似に加えて祝日CSV除外を前処理ポリシーへ組み込んだ
  - `tests/test_calendar_policy.py` と `tests/test_raw_csv_e2e.py` に祝日ケースを追加し回帰を固定した
  - `configs/jpx_holidays_sample.csv` を追加し運用サンプルを用意した
- 意図的に後回しにしたこと:
  - 公式JPXサイトからの自動取得
