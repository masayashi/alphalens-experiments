# 実行: バックオフジッター・追加分析指標・トークン運用方針（Phase 9）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` にバックオフジッター（`retry_jitter_ratio`）を追加した。
2. `Retry-After` のHTTP-date形式解釈を追加した（秒形式・HTTP-date両対応）。
3. `run_analysis.py` の分析サマリーに追加指標を実装した。
   - スプレッドt値
   - スプレッド年率換算
4. `tests/test_data_adapters.py` にジッター動作とHTTP-date再試行の回帰テストを追加した。
5. `tests/test_raw_csv_e2e.py` で新規サマリー列（t値・年率換算）を検証した。
6. `docs/specs/api-token-operation-policy.md` を追加し、OSシークレットストア連携方針を文書化した。
7. README を更新した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - バックオフの柔軟性（ジッター・Retry-After date）を強化した
  - 分析サマリーを実務的な指標まで拡張した
  - シークレット運用の方針を仕様化した
- 意図的に後回しにしたこと:
  - OSシークレットストアの実コード連携
  - provider別の細かなレート制限ポリシー
