# 計画: 実データ入力向け E2E 拡張（Raw CSV 導線）

## ゴール

- 実データ想定の Raw CSV から Alphalens 実行までを一気通貫で再現できる導線を追加する。
- 回帰テストで導線を固定し、品質ゲート全通過を確認する。

## スコープ

- 対象:
  - Raw CSV を processed parquet（prices/factor）へ変換するスクリプト追加
  - `load_prices` の CSV 入力対応
  - Raw CSV 変換 + `run_analysis` の E2E テスト追加
- 対象外:
  - 外部 API / DB 接続
  - 本番向けデータクリーニング（銘柄名正規化、企業アクション補正の高度化）

## チェック

- Lint: `uv run ruff check .`
- 型検査: `uv run mypy`
- Tests: `uv run pytest -q`
- Windows 権限制約環境: `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 手順

1. Raw CSV 変換スクリプトを追加し、long/wide の最低限入力を処理できるようにする。
2. `load_prices` を拡張して CSV / parquet 両対応にする。
3. E2E テストを追加して Raw CSV 導線を検証する。
4. 品質ゲートを実行し、実行記録とセッション状態を更新する。

## リスク

- リスク:
  - CSV 形式の揺れ（long/wide 判定）で誤解釈が起こる
  - E2E テストが作業ディレクトリ依存になる
- 緩和策:
  - long 形式は `date,asset,close` を必須化し、wide 形式は先頭列を `date` として扱う
  - テストは `tmp_path` 配下に入出力を閉じ、コマンドに絶対パスを渡す
