# 実行: 外部 API / DB 入力アダプタの雛形追加

## 入力

- 計画参照: `docs/plans/2026-03-20-data-adapter-skeleton-plan.md`
- ブランチ: `master`

## 変更内容

1. 価格データアダプタの共通インターフェースと雛形を追加した。
2. アダプタ選択実行スクリプトを追加した。
3. CSVアダプタと未実装例外の回帰テストを追加した。

## 検証

- `powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1`

## 結果

- 完了したこと:
  - `run_quality_gate` により `ruff check` / `mypy` / `pytest` の全通過を確認した
  - CSV/API/DB の入力拡張点を `data_adapters.py` に統一した
  - `tests/test_data_adapters.py` で CSV 読込と雛形例外の回帰を固定した
- 意図的に後回しにしたこと:
  - 実 API 接続と DB クエリ実装
