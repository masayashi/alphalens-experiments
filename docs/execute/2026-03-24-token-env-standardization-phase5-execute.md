# 実行: APIトークン環境変数運用の標準化（Phase 5）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `ApiPriceAdapter(provider=httpcsv)` をトークン必須に変更した。
2. `fetch_prices_with_adapter.py` / `run_real_data_pipeline.py` に `--auth-token-env` を追加した。
3. CLI のトークン解決順を `--auth-token` 優先、未指定時は環境変数参照に統一した。
4. `tests/test_data_adapters.py` にトークン必須の回帰テストを追加した。
5. README の認証付きAPI例を環境変数運用へ更新した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - 認証付きAPIの平文トークン直書きを避ける標準運用を整備した
  - トークン未設定時の失敗をテストで固定した
- 意図的に後回しにしたこと:
  - OSのシークレットストア連携
  - レート制限エラー向け指数バックオフの高度化
