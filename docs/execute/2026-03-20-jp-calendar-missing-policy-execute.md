# 実行: 日本株カレンダーと欠損日の扱いを仕様固定

## 入力

- 計画参照: `docs/plans/2026-03-20-jp-calendar-missing-policy-plan.md`
- ブランチ: `master`

## 変更内容

1. 価格前処理ポリシー実装を `calendar_policy.py` として追加した。
2. `prepare_raw_prices_csv.py` へポリシー適用を組み込んだ。
3. 仕様ドキュメントと回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` により `ruff check` / `mypy` / `pytest` の全通過を確認した
  - 平日フィルタと欠損日除外のポリシーを `calendar_policy.py` に固定した
  - `tests/test_calendar_policy.py` と `tests/test_raw_csv_e2e.py` で回帰を固定した
  - 仕様書 `docs/specs/jp-calendar-missing-policy.md` を追加した
- 意図的に後回しにしたこと:
  - 祝日・休場日の厳密判定
