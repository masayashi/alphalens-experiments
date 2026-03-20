# 実行: 比較レポート可視化テンプレート追加

## 入力

- 計画参照: `docs/plans/2026-03-20-visualize-factor-summary-plan.md`
- ブランチ: `master`

## 変更内容

1. `plot_factor_summary.py` を追加し、比較CSVからPNGを生成できるようにした。
2. 画像生成の回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` により `ruff check` / `mypy` / `pytest` の全通過を確認した
  - `reports` 配下へ比較指標のPNGを生成する可視化導線を追加した
  - `tests/test_plot_factor_summary.py` で画像生成を回帰固定した
- 意図的に後回しにしたこと:
  - インタラクティブな可視化
