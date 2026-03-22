# 日本株価格データのカレンダー・欠損ポリシー

## 目的

Alphalens 入力前の価格データを、再現可能なルールで正規化する。

## 現行ポリシー（v3）

1. 営業日近似として平日（Mon-Fri）のみを採用する。
2. 任意の祝日CSVが指定された場合、その日付行を除外する。
3. 祝日CSVはローカルファイル指定に加え、URLから自動取得して保存できる。
4. 銘柄のいずれかに欠損値がある日は、その日付行を丸ごと除外する。

## 祝日CSV仕様

- 必須列: `date`（入力側は `date/Date/日付/年月日` を許容し、保存時に `date` へ標準化）
- 例: `configs/jpx_holidays_sample.csv` / `configs/jpx_holidays_latest.csv`
- CLI 指定:
  - `scripts/prepare_raw_prices_csv.py --jpx-holidays-csv <path>`
  - `scripts/prepare_raw_prices_csv.py --jpx-holidays-url <url> --jpx-holidays-out <path>`

## 適用箇所

- 実装:
  - `src/alphalens_experiments/calendar_policy.py`
  - `src/alphalens_experiments/holiday_fetcher.py`
- 呼び出し:
  - `scripts/prepare_raw_prices_csv.py`
  - `scripts/run_real_data_pipeline.py`
  - `scripts/fetch_jpx_holidays_csv.py`
- 検証:
  - `tests/test_calendar_policy.py`
  - `tests/test_holiday_fetcher.py`
  - `tests/test_raw_csv_e2e.py`
  - `tests/test_real_data_pipeline.py`

## 既知の制約

- 公式ソースURL自体は運用時に指定する（本リポジトリではURLを固定しない）。
- 欠損補完（前日値埋め等）は行わず、日付行除外を選択している。

## 将来拡張

- 祝日CSVの署名検証やハッシュ検証を追加する。
- 欠損ポリシーを `drop/ffill/interpolate` から選択可能にする。
