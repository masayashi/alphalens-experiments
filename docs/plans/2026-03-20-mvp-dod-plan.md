# 計画: MVP DoD 固定と検証強化（2026-03-20）

## ゴール

- 日本株サンプルデータで Alphalens の分析パイプラインを再現可能に実行し、成果物を `reports/` に出力できる状態を完了条件として固定する。
- 完了判定を `ruff check / mypy / pytest` 全通過で明示する。

## スコープ

- 対象:
  - MVP の DoD（Definition of Done）を文書化
  - `data_loader` の入力整形に関するテスト追加
  - 実行記録（Execute）とセッション状態更新
- 対象外:
  - 実データ（外部 API / DB）連携
  - セクター中立化、売買コスト考慮、複数因子比較の高度化

## チェック

- Lint: `uv run ruff check .`
- 型検査: `uv run mypy`
- Tests: `uv run pytest -q`
- Windows 権限制約環境: `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 手順

1. 計画書を作成し、MVP の完了条件（成果物・入力形式・検証条件）を明文化する。
2. `data_loader` の境界条件（DatetimeIndex 変換、MultiIndex 正規化、必須カラム欠落）をテストで固定する。
3. Execute 記録を作成し、品質ゲートを実行して結果を反映する。
4. `state/session_progress.json` を更新して次アクションを明示する。

## リスク

- リスク:
  - ローカル環境差分により `uv sync` が失敗する可能性
  - Parquet 入出力の依存差分でテストが不安定になる可能性
- 緩和策:
  - `scripts/run_quality_gate.ps1` を利用し、キャッシュをリポジトリ内へ固定する
  - テストは `tmp_path` を使って自己完結させる
