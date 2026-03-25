# APIトークン運用方針

## 目的

認証付きAPI連携で、トークンの平文露出を最小化しつつ、ローカル実行とCI実行を両立する。

## 現行実装

- CLIの解決順は `--auth-token` > `--auth-token-env` > `keyring`。
- `--auth-token-env` の既定値は `ALPHALENS_API_TOKEN`。
- `--auth-token-keyring-service` / `--auth-token-keyring-username` で keyring 参照先を指定できる。
- `provider=httpcsv` はトークン未設定時に即時失敗する。

## 推奨運用

1. ローカル開発（Windows）

- セッション限定で環境変数を設定:

```powershell
$env:ALPHALENS_API_TOKEN = "<TOKEN>"
```

- 永続化する場合は OS シークレットストア（keyring バックエンド）を優先し、平文ファイル保存を避ける。

2. CI/CD

- CI の Secret 機能（GitHub Actions Secrets 等）で `ALPHALENS_API_TOKEN` を注入する。
- ワークフロー上のログ出力でトークンを展開しない。

## OSシークレットストア連携

- 候補:
  - Windows Credential Manager
  - macOS Keychain
  - Linux Secret Service
- 実装方針:
  - 既定サービス名は `alphalens-experiments/api-token`。
  - 既定ユーザー名は `default`。
  - keyring が未導入/未設定でも処理継続し、最終的にトークン未解決として失敗させる。

### Windows 導入手順（例）

```powershell
uv run python -m pip install keyring keyrings.alt
uv run python -c "import keyring; keyring.set_password('alphalens-experiments/api-token','default','<TOKEN>')"
```

### macOS 導入手順（例）

```bash
uv run python -m pip install keyring
uv run python -c "import keyring; keyring.set_password('alphalens-experiments/api-token','default','<TOKEN>')"
```

### Linux 導入手順（例）

```bash
uv run python -m pip install keyring secretstorage
uv run python -c "import keyring; keyring.set_password('alphalens-experiments/api-token','default','<TOKEN>')"
```

## セキュリティガード

- トークン値を例外メッセージ・ログに出さない。
- 設定ファイルへトークンを保存しない。
- issue / docs / commit message に実トークンを記載しない。
