# 日本株価格データのカレンダー・欠損ポリシー

## 目的

Alphalens 入力前の価格データを、再現可能なルールで正規化する。

## 現行ポリシー（v2）

1. 営業日近似として平日（Mon-Fri）のみを採用する。
2. 任意の祝日CSVが指定された場合、その日付行を除外する。
3. 銘柄のいずれかに欠損値がある日は、その日付行を丸ごと除外する。

## 祝日CSV仕様

- 必須列: `date`
- 例: `configs/jpx_holidays_sample.csv`
- CLI 指定: `scripts/prepare_raw_prices_csv.py --jpx-holidays-csv <path>`

## 適用箇所

- 実装: `src/alphalens_experiments/calendar_policy.py`
- 呼び出し: `scripts/prepare_raw_prices_csv.py`
- 検証: `tests/test_calendar_policy.py` と `tests/test_raw_csv_e2e.py`

## 既知の制約

- 祝日CSVは手動管理で、公式JPXサイトとの同期は自動化していない。
- 欠損補完（前日値埋め等）は行わず、日付行除外を選択している。

## 将来拡張

- JPX公式データの自動取得ジョブを追加する。
- 欠損ポリシーを `drop/ffill/interpolate` から選択可能にする。
