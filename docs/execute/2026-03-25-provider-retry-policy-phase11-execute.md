# 実行: provider別再試行ポリシーの細分化（Phase 11）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` に provider別再試行ポリシー分岐を追加した。
2. `httpcsv` は `Retry-After` / ジッターを利用する。
3. `stooq` は `Retry-After` とジッターを無効化し、単純バックオフを使う。
4. `tests/test_data_adapters.py` に stooqポリシー回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - provider別に待機ポリシーを切り替え可能にした
  - `stooq` の単純バックオフ方針をテストで固定した
- 意図的に後回しにしたこと:
  - providerごとのHTTPステータス再試行条件を外部設定化する
