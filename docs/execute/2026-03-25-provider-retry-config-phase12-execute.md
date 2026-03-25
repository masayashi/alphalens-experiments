# 実行: provider別再試行条件の外部設定化（Phase 12）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` に外部再試行ポリシー読込を追加した。
   - 既定: `configs/api_retry_policy.json`
   - 上書き: `ALPHALENS_RETRY_POLICY_PATH`
2. provider別ポリシーを設定ファイルで管理可能にした。
   - `retryable_http_statuses`
   - `use_retry_after`
   - `use_jitter`
3. `configs/api_retry_policy.json` を追加した。
4. `tests/test_data_adapters.py` に外部ポリシー反映の回帰テストを追加した。
5. README に再試行ポリシー設定ファイルを追記した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - provider別再試行条件をコード変更なしで調整可能にした
  - 環境変数でポリシーファイル差し替え可能にした
- 意図的に後回しにしたこと:
  - 設定スキーマ検証（jsonschema等）
