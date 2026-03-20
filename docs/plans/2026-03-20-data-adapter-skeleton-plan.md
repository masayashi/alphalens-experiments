# 計画: 外部 API / DB 入力アダプタの雛形追加

## ゴール

- 実データ入力の拡張点をコードとして明示し、CSV/API/DB を同一インターフェースで扱える土台を追加する。

## スコープ

- 対象:
  - 価格データ取得アダプタのインターフェース定義
  - CSV アダプタ実装
  - API/DB アダプタの雛形（未実装例外）
  - 最小テスト
- 対象外:
  - 実際の外部 API 接続
  - 実DBへのクエリ実装

## チェック

- Lint: `uv run ruff check .`
- 型検査: `uv run mypy`
- Tests: `uv run pytest -q`
- Windows 権限制約環境: `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 手順

1. `src` にアダプタ抽象と雛形実装を追加する。
2. CLI スクリプトでアダプタ選択実行を可能にする。
3. テストで CSV アダプタと未実装例外を固定する。
4. 品質ゲート実行後に Execute と session を更新する。

## リスク

- リスク:
  - 雛形だけでは即時利用できない
- 緩和策:
  - 例外メッセージに実装ポイントを明記し、次タスクへ接続する
