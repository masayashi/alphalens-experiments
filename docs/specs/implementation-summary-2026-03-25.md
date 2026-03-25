# 実装サマリー（2026-03-25）

## 1. 何が可能になったか

- 実データ導線の一気通貫実行
  - `取得 -> 前処理 -> ファクター生成 -> Alphalens分析 -> 比較CSV/PNG出力` を1コマンドで実行可能
- 入力ソースの拡張
  - `csv` / `api(stooq, httpcsv)` / `db(sqlite)` に対応
- 認証付きAPI運用
  - トークン解決順: `--auth-token` > `--auth-token-env` > `keyring`
- JPX祝日対応
  - 祝日CSV手動指定 + URL自動取得に対応
- 分析レポートの拡張
  - `analysis_summary.csv` に IC、分位リターン、上位-下位スプレッド、t値、年率換算を出力
- API再試行の運用強化
  - 指数バックオフ、`Retry-After`（秒/HTTP-date）、ジッター
  - provider別ポリシー切替（`stooq` / `httpcsv`）
  - 再試行ポリシーを `configs/api_retry_policy.json` で外部設定可能
  - 設定は jsonschema 相当で厳格検証（不正時は明示エラー）

## 2. まず試す最短手順

### 2-1. サンプルデータで分析

```powershell
uv run python scripts\generate_sample_jp_data.py
uv run python -m alphalens_experiments.run_analysis `
  --prices data\processed\sample_prices_jp.parquet `
  --factor data\processed\sample_factor_jp.parquet `
  --periods 1 5 10 `
  --skip-tearsheet
```

確認ポイント:
- `reports/tearsheet_output.txt`
- `reports/analysis_summary.csv`

### 2-2. 実データCSVで一気通貫

```powershell
uv run python scripts\run_real_data_pipeline.py `
  --source csv `
  --path data\raw\your_prices.csv `
  --skip-tearsheet
```

確認ポイント:
- `data/raw/adapter_loaded_prices.csv`
- `data/processed/prepared_prices_jp.parquet`
- `data/processed/prepared_factor_jp.parquet`
- `reports/analysis_summary.csv`
- `reports/multi_factor_summary.csv`
- `reports/multi_factor_summary.png`

## 3. API利用の試し方

### 3-1. stooq（認証なし）

```powershell
uv run python scripts\run_real_data_pipeline.py `
  --source api `
  --provider stooq `
  --symbols 7203.T,6758.T,9432.T `
  --start 2024-01-01 `
  --end 2025-12-31 `
  --skip-tearsheet
```

### 3-2. httpcsv（認証あり）

```powershell
$env:ALPHALENS_API_TOKEN = "<TOKEN>"
uv run python scripts\run_real_data_pipeline.py `
  --source api `
  --provider httpcsv `
  --symbols 7203.T,6758.T `
  --api-url "https://api.example.com/prices?symbol={symbol}" `
  --auth-token-env "ALPHALENS_API_TOKEN" `
  --auth-token-keyring-service "alphalens-experiments/api-token" `
  --auth-token-keyring-username "default" `
  --skip-tearsheet
```

## 4. 再試行ポリシー調整

設定ファイル: `configs/api_retry_policy.json`

```json
{
  "stooq": {
    "retryable_http_statuses": [429, 500, 502, 503, 504],
    "use_retry_after": false,
    "use_jitter": false
  },
  "httpcsv": {
    "retryable_http_statuses": [429, 500, 502, 503, 504],
    "use_retry_after": true,
    "use_jitter": true
  }
}
```

一時的に別ファイルを使う場合:

```powershell
$env:ALPHALENS_RETRY_POLICY_PATH = "C:\path\to\retry_policy.json"
```

## 5. 関連資料

- 主要README: `README.md`
- APIトークン運用: `docs/specs/api-token-operation-policy.md`
- API再試行ポリシー仕様: `docs/specs/api-retry-policy-schema.md`
- カレンダー/欠損ポリシー: `docs/specs/jp-calendar-missing-policy.md`
