# 実行: jsonschema導入とOS別keyring手順整備（Phase 14）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` の再試行ポリシー検証を `jsonschema` ベースへ切り替えた。
2. 再試行ポリシースキーマをコード内定義し、不正時は `RuntimeError` で明示失敗とした。
3. `tests/test_data_adapters.py` の不正設定テストを jsonschemaエラーメッセージ系に更新した。
4. `pyproject.toml` に `jsonschema` を明示依存として追加し、`uv.lock` を更新した。
5. `docs/specs/api-token-operation-policy.md` に OS別 keyring 導入手順（Windows/macOS/Linux）を追記した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - 再試行ポリシーの検証を jsonschema で厳格化した
  - keyring バックエンド導入のOS別手順を文書化した
- 意図的に後回しにしたこと:
  - keyring バックエンド導入の自動化スクリプト化
