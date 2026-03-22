# 計画: 実株価データで Alphalens 分析と結果出力を完走する実装

## ゴール

- 日本株の実株価データを使って、`取得 -> 前処理 -> ファクター生成 -> Alphalens分析 -> 結果出力` を再現可能に実行できる状態にする。
- ローカル実行だけでなく、回帰テストで最低限の導線を固定する。

## スコープ

- 対象:
  - 不足実装の明確化（現状調査の記録）
  - API/DB アダプタの実接続（段階実装）
  - 実データ E2E 実行スクリプトの整備
  - 分析結果のファイル出力（CSV/PNG/ログ）の標準化
  - 実データ導線のテスト追加
- 対象外:
  - 有料データベンダー固有の認証情報管理の本番運用
  - 高度な中立化（業種中立/サイズ中立）や売買コスト最適化の本格実装

## 調査結果（不足実装）

- 1. `src/alphalens_experiments/data_adapters.py` の `ApiPriceAdapter` / `DatabasePriceAdapter` が `NotImplementedError` のまま。
- 2. `scripts/fetch_prices_with_adapter.py` は入口のみで、実データ取得時のプロバイダ別パラメータ検証・リトライ・失敗時ログが不足。
- 3. 実データ向けの一気通貫 CLI がないため、`fetch -> prepare_raw_prices_csv -> run_analysis -> compare/plot` が手作業連結になる。
- 4. `run_analysis.py` の出力は `tearsheet_output.txt` 中心で、主要指標を機械可読な CSV で残す仕組みが不足。
- 5. 実データ接続を想定した E2E テスト（モック API / 一時 DB を使う統合テスト）が未整備。
- 6. JPX 祝日データは CSV 注入方式までで、公式ソース自動取得ジョブが未実装。

## チェック

- Lint/Format/型/テスト: `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`
- タスク固有の追加チェック:
  - `uv run python scripts/fetch_prices_with_adapter.py --source csv --path <raw_csv> --out data/raw/adapter_loaded_prices.csv`
  - `uv run python scripts/prepare_raw_prices_csv.py --raw-prices data/raw/adapter_loaded_prices.csv --jpx-holidays-csv configs/jpx_holidays_sample.csv`
  - `uv run python -m alphalens_experiments.run_analysis --prices data/processed/prepared_prices_jp.parquet --factor data/processed/prepared_factor_jp.parquet --periods 1 5 10`
  - `uv run python scripts/run_multi_factor_template.py --prices data/processed/prepared_prices_jp.parquet`
  - `uv run python scripts/plot_factor_summary.py --summary reports/multi_factor_summary.csv`

## 手順

1. `data_adapters.py` を段階実装する（Phase 1: `csv` 強化、Phase 2: `api` 実装、Phase 3: `db` 実装）。
2. `scripts/fetch_prices_with_adapter.py` にソース別引数バリデーション、例外時ログ、出力整形（日付/銘柄型）を追加する。
3. `scripts/run_real_data_pipeline.py`（新規）を追加し、`fetch -> prepare -> analysis -> compare -> plot` を1コマンド化する。
4. `run_analysis.py` を拡張し、主要結果（行数、欠損率、IC集計など）を `reports/analysis_summary.csv` に出力する。
5. テストを追加する:
   - `tests/test_data_adapters.py` に API/DB 実装テスト（モック/一時DB）を追加
   - `tests/test_raw_csv_e2e.py` または新規 E2E テストでパイプライン全体を固定
6. JPX 祝日自動取得の最小設計を `docs/specs` に追加し、後続実装タスクへ分割する。
7. 品質ゲートを実行し、`docs/execute` と `state/session_progress.json` を更新する。

## リスク

- リスク:
  - 外部 API の利用規約・レート制限でテストが不安定化する
  - 実データ欠損や銘柄コード揺れで分析前処理が落ちる
  - 可視化依存（matplotlib backend）で CI/Windows の差分が出る
- 緩和策:
  - API テストは通信をモックし、オンライン接続は任意の手動検証に分離する
  - 入力正規化関数とデータ品質チェックを先に実装して異常値を早期検知する
  - 画像生成テストは `Agg` 固定とファイル存在検証に限定する
