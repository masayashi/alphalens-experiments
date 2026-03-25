# 実行: OSシークレットストア解決導線の実装（Phase 10）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `secret_resolver.py` を追加し、トークン解決順を `explicit > env > keyring` に統一した。
2. `fetch_prices_with_adapter.py` と `run_real_data_pipeline.py` に keyring オプションを追加した。
   - `--auth-token-keyring-service`
   - `--auth-token-keyring-username`
3. `tests/test_secret_resolver.py` を追加して解決優先順位を回帰固定した。
4. 既存仕様書 `docs/specs/api-token-operation-policy.md` を現行実装に合わせて更新した。
5. README を更新し、認証付きAPI実行例に keyring オプションを追記した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - OSシークレットストア（keyring）を使ったトークン解決導線を実装した
  - トークン解決優先順位をコードとテストで統一した
- 意図的に後回しにしたこと:
  - keyringバックエンド導入手順のOS別自動化
  - provider別の再試行ポリシー細分化
