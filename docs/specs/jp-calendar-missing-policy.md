# 日本株価格データのカレンダー・欠損ポリシー

## 目的

Alphalens 入力前の価格データを、再現可能なルールで正規化する。

## 現行ポリシー（v1）

1. 営業日近似として平日（Mon-Fri）のみを採用する。
2. 銘柄のいずれかに欠損値がある日は、その日付行を丸ごと除外する。

## 適用箇所

- 実装: `src/alphalens_experiments/calendar_policy.py`
- 呼び出し: `scripts/prepare_raw_prices_csv.py`
- 検証: `tests/test_calendar_policy.py` と `tests/test_raw_csv_e2e.py`

## 既知の制約

- 祝日・取引所休場日は v1 では厳密に判定しない（平日ベース近似）。
- 欠損補完（前日値埋め等）は行わず、日付行除外を選択している。

## 将来拡張

- JPX カレンダー連携で休場日を厳密化する。
- 欠損ポリシーを `drop/ffill/interpolate` から選択可能にする。
