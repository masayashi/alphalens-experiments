# 計画: 比較レポート可視化テンプレート追加

## ゴール

- 因子比較サマリーCSVから、確認しやすい可視化PNGを自動生成できるテンプレートを追加する。

## スコープ

- 対象:
  - 可視化スクリプト追加
  - 最小テスト追加
  - 実行記録更新
- 対象外:
  - インタラクティブUI
  - 高度なダッシュボード

## チェック

- Lint: `uv run ruff check .`
- 型検査: `uv run mypy`
- Tests: `uv run pytest -q`
- Windows 権限制約環境: `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 手順

1. CSVから `mean_abs_ic` を描画する可視化スクリプトを追加する。
2. 画像生成の回帰テストを追加する。
3. 品質ゲート実行後、Executeと状態を更新する。

## リスク

- リスク:
  - matplotlib backend差分で画像生成が失敗する
- 緩和策:
  - `Agg` バックエンドを明示してヘッドレス実行に固定する
