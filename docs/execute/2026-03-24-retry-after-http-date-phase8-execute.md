# 実行: Retry-After HTTP-date 形式対応（Phase 8）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` の Retry-After 解釈に HTTP-date 形式を追加した。
2. Retry-After が数値でない場合、HTTP-date をパースして現在時刻との差分秒を待機時間に採用するようにした。
3. 不正な Retry-After 値は従来どおり指数バックオフへフォールバックするようにした。
4. `tests/test_data_adapters.py` に HTTP-date ヘッダを使う回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - Retry-After の秒数形式とHTTP-date形式の両方を扱えるようにした
  - HTTP-date の待機秒計算（5秒）をテストで固定した
- 意図的に後回しにしたこと:
  - バックオフにジッター追加
  - provider別の再試行ポリシー細分化
