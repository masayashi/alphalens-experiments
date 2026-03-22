# 実行: 認証付きAPIアダプタ追加（Phase 3）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `ApiPriceAdapter` に `provider=httpcsv` を追加し、`--api-url` と `auth header` 付き取得を実装した。
2. `build_adapter` に認証パラメータ（token/header名/prefix）を追加した。
3. `fetch_prices_with_adapter.py` と `run_real_data_pipeline.py` に認証付きAPI用オプションを追加した。
4. `tests/test_data_adapters.py` に認証ヘッダ付与の回帰テストを追加した。
5. README に認証付きAPI利用例を追記した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - 認証付きAPI（httpcsv）を既存パイプラインへ統合した
  - APIのURLテンプレート（`{symbol}`）置換で銘柄ごと取得を可能にした
- 意図的に後回しにしたこと:
  - トークンの安全保管（環境変数専用強制、Secret Manager連携）
  - レート制限ヘッダの厳密解釈と指数バックオフ
