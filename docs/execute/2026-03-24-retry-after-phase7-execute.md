# 実行: Retry-After ヘッダ対応の待機制御追加（Phase 7）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` に `Retry-After` 優先の待機時間計算を追加した。
2. 再試行可能HTTPエラー時は `Retry-After` が有効ならその秒数を採用し、なければ指数バックオフにフォールバックするようにした。
3. `tests/test_data_adapters.py` に `Retry-After=3` を優先採用する回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - `Retry-After` を尊重するAPI待機制御を実装した
  - 既存の指数バックオフはフォールバックとして維持した
- 意図的に後回しにしたこと:
  - `Retry-After` のHTTP-date形式対応
  - ジッター付きバックオフ
