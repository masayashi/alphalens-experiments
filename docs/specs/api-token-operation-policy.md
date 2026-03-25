# APIトークン運用方針（案）

## 目的

認証付きAPI連携で、トークンの平文露出を最小化しつつ、ローカル実行とCI実行を両立する。

## 現行実装

- CLIは `--auth-token` よりも `--auth-token-env`（既定: `ALPHALENS_API_TOKEN`）運用を推奨。
- `provider=httpcsv` はトークン未設定時に即時失敗する。

## 推奨運用

1. ローカル開発（Windows）

- セッション限定で環境変数を設定:

```powershell
$env:ALPHALENS_API_TOKEN = "<TOKEN>"
```

- 永続化する場合は OS シークレットストアの利用を優先し、平文ファイル保存を避ける。

2. CI/CD

- CI の Secret 機能（GitHub Actions Secrets 等）で `ALPHALENS_API_TOKEN` を注入する。
- ワークフロー上のログ出力でトークンを展開しない。

## OSシークレットストア連携（次段階）

- 候補:
  - Windows Credential Manager
  - macOS Keychain
  - Linux Secret Service
- 実装方針:
  - 優先順位を `--auth-token` > `環境変数` > `OSシークレットストア` とする。
  - ストア参照キーは `alphalens-experiments/api-token` を既定値として統一する。

## セキュリティガード

- トークン値を例外メッセージ・ログに出さない。
- 設定ファイルへトークンを保存しない。
- issue / docs / commit message に実トークンを記載しない。
