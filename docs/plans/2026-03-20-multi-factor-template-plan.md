# 計画: 複数ファクター比較テンプレート追加

## ゴール

- 複数ファクターを同一価格データ上で比較し、最小レポートを `reports/` に出力できるテンプレートを追加する。

## スコープ

- 対象:
  - 因子比較ロジックの追加
  - 比較実行スクリプトの追加
  - 最小回帰テスト追加
- 対象外:
  - 高度な統計検定や可視化ダッシュボード
  - 本番運用のモデル選定フロー

## チェック

- Lint: `uv run ruff check .`
- 型検査: `uv run mypy`
- Tests: `uv run pytest -q`
- Windows 権限制約環境: `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 手順

1. 複数因子比較の集計関数を `src` に追加する。
2. サンプル因子（モメンタム/ランダム）比較スクリプトを追加する。
3. 比較結果の回帰テストを追加する。
4. 品質ゲート実行後に Execute と session を更新する。

## リスク

- リスク:
  - データ長が短いと forward return で欠損が増える
- 緩和策:
  - スクリプトに `max_loss` 引数を持たせ、テストでは高めに設定する
