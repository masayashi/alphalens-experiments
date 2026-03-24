# 実行: APIレート制限向け指数バックオフ実装（Phase 6）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` のHTTP取得リトライを改善した。
2. `HTTPError` のうち `429/500/502/503/504` を再試行対象にした。
3. 待機時間を指数バックオフ（`retry_wait_seconds * 2^attempt`）へ変更した。
4. `empty response` のみ `ValueError` 再試行対象とし、構造不正などは即時失敗にした。
5. `tests/test_data_adapters.py` に指数バックオフの回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - レート制限・一時障害時に指数バックオフ再試行するようになった
  - バックオフ待機秒（0.2, 0.4）をテストで固定した
- 意図的に後回しにしたこと:
  - `Retry-After` ヘッダの解釈
  - ジッター付きバックオフ
