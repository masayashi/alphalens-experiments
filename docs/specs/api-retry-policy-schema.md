# API再試行ポリシー設定仕様

## ファイル

- 既定: `configs/api_retry_policy.json`
- 上書き: 環境変数 `ALPHALENS_RETRY_POLICY_PATH`

## ルート構造

- JSON object
- key: provider名（例: `stooq`, `httpcsv`）
- value: providerごとの設定object

## 設定キー

- `retryable_http_statuses`:
  - 型: `int[]`
  - 範囲: `100..599`
- `use_retry_after`:
  - 型: `bool`
- `use_jitter`:
  - 型: `bool`

## バリデーション

- 未知キーはエラー
- 型不一致はエラー
- provider object が空はエラー
- 不正設定時は `RuntimeError` で起動時に明示失敗

## 補足

- 設定がないproviderはコード内デフォルトを使用
- `stooq` は既定で `Retry-After/jitter` 無効
- `httpcsv` は既定で `Retry-After/jitter` 有効
