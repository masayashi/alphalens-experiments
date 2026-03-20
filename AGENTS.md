# 基本ルール
やりとりは日本語で行うこと
資料は日本語で記載すること

# プロジェクト概要
Alphalensを使用して株式の分析を行うためのプロジェクト
対象は日本株

# 開発ルール

## 参照順序（真実の所在）

- 実行可能なチェックを最優先し、文章だけの説明を優先しないこと。
- ハーネス方針: `docs/adr/ADR-0001-harness-policy.md`
- セットアップと実行手順: `README.md`
- セッション状態: `state/session_progress.json`

## 高速ループ（必須）

1. `uv sync --extra dev`
2. `uv run ruff format .`
3. `uv run ruff check .`
4. `uv run pytest -q`

## タスク進行

- まず `docs/templates/PLAN.md` で計画する。
- 次に `docs/templates/EXECUTE.md` で実行する。
- 変更は小さくし、必ず検証可能にする。

## セーフティレール

- 秘密情報や生資格情報は絶対にコミットしない。
- モデルの判断より決定論的ツールを優先する。
- 発見したバグ/回帰には必ずテストを追加する。
- ADR の履歴は編集せず、新しい ADR で supersede する。

## 完了条件

- lint と tests が通って初めてタスク完了とする。
