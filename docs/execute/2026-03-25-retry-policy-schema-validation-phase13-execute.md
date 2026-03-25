# 実行: 再試行ポリシーのスキーマ検証追加（Phase 13）

## 入力

- 計画参照: `docs/plans/2026-03-22-real-data-alphalens-e2e-plan.md`
- ブランチ: `master`

## 変更内容

1. `data_adapters.py` に再試行ポリシーの厳格バリデーションを追加した。
   - 未知キー禁止
   - 型検証
   - HTTPステータス範囲検証
2. 不正設定時に `RuntimeError` で明示失敗するようにした。
3. `tests/test_data_adapters.py` に不正スキーマ回帰テストを追加した。
4. `docs/specs/api-retry-policy-schema.md` を追加した。
5. README に再試行ポリシー仕様の参照を追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` で `ruff format/check` / `mypy` / `pytest` の全通過を確認した
  - 再試行ポリシー設定の不整合を早期に検知可能にした
  - 設定仕様を文書化した
- 意図的に後回しにしたこと:
  - 設定ファイルのjsonschema自動検証
