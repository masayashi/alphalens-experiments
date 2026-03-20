# 基本ルール
やりとりは日本語で行うこと
資料とコミットログは日本語で記載すること
作業が完了したら必ずコミットしてプッシュすること

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
4. `uv run mypy`
5. `uv run pytest -q`
6. Windows 権限制約環境では `scripts/run_quality_gate.ps1` を優先する。

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

- Stop 条件: `ruff check` / `mypy` / `pytest` の全通過。
- 上記が通らない場合はタスクを完了扱いにしない。

## ローカルフック

- `scripts/setup_local_harness.ps1` で `core.hooksPath=.githooks` を設定する。
- `.githooks/pre-commit.bat` はリポジトリ内キャッシュを使って品質ゲートを実行する。
