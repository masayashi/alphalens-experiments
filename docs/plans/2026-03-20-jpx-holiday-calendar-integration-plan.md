# 計画: JPX 祝日カレンダー連携（CSV 注入方式）

## ゴール

- 日本株価格前処理に祝日除外を組み込み、平日近似から一段進んだ取引日フィルタを実現する。
- 祝日データは CSV から注入可能にし、将来の公式データ連携へ差し替えやすくする。

## スコープ

- 対象:
  - 祝日CSV読み込み関数の追加
  - `apply_jp_price_policy` への祝日除外オプション追加
  - `prepare_raw_prices_csv.py` の `--jpx-holidays-csv` 対応
  - 回帰テスト追加
  - 仕様ドキュメント更新
- 対象外:
  - 公式JPXサイトからの自動取得
  - 月次自動更新

## チェック

- Lint: `uv run ruff check .`
- 型検査: `uv run mypy`
- Tests: `uv run pytest -q`
- Windows 権限制約環境: `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 手順

1. 祝日CSV読込・祝日除外ロジックを `calendar_policy.py` に追加する。
2. `prepare_raw_prices_csv.py` へ祝日CSV指定オプションを追加する。
3. 単体テストとE2Eテストで祝日除外の回帰を固定する。
4. 品質ゲート通過後、Executeと状態を更新する。

## リスク

- リスク:
  - 祝日CSVのフォーマット揺れで読み込み失敗
- 緩和策:
  - 必須列を `date` として明示し、不備時は明確な `ValueError` を返す
