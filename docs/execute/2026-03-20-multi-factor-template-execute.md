# 実行: 複数ファクター比較テンプレート追加

## 入力

- 計画参照: `docs/plans/2026-03-20-multi-factor-template-plan.md`
- ブランチ: `master`

## 変更内容

1. 因子比較ロジックを `factor_compare.py` に追加した。
2. 比較実行スクリプト `run_multi_factor_template.py` を追加した。
3. 因子比較の回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` により `ruff check` / `mypy` / `pytest` の全通過を確認した
  - 2因子（モメンタム/ランダム）の比較サマリーを出力するテンプレートを追加した
  - `tests/test_factor_compare.py` で比較集計の回帰を固定した
- 意図的に後回しにしたこと:
  - 高度な統計検定や可視化の自動化
