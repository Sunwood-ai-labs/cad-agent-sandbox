# Case Layout

このリポジトリは、別テーマの CAD ベンチマークを `cases/<slug>/` として追加できる構成にしています。

## 公開で追跡するもの

- ケース固有の `README.md`、`docs/`、`scripts/`、CAD ソース
- 軽量な比較レポート CSV / Markdown
- レポート用スクリーンショット
- HyperFrames の動画ソースと素材

## 追跡しないもの

- `cases/*/outputs/`
- `cases/*/reports/encoding_check.csv` などの再生成ログ
- `cases/*/reports/video_views/`
- `cases/*/videos/*/renders/`
- `cases/*/videos/*/qa_frames/`
- `cases/*/videos/*/.hyperframes/`
- `cases/*/tools/`
- `cases/*/node_modules/`

## 現在の tracked ケース

- [cases/cupboard/](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/cupboard): 基本カップボード
- [cases/kitchen-trash-cupboard/](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard): ゴミ箱 3 台対応キッチンカップボード
- [cases/kitchen-trash-cupboard-concept1/](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard-concept1): コンセプト画像に合わせたキッチンカップボード派生ケース

## ケースを追加する手順

1. 既存ケースを複製します。
2. `README.md` と `docs/SETUP_AND_USAGE.md` のテーマ名、仕様、出力先を更新します。
3. `cupboard_benchmark/spec.py` に寸法と部品仕様を集約します。
4. `videos/<slug>-comparison/` の slug をケース固有にします。
5. ルートで `uv run cases\cupboard\scripts\verify_text_encoding.py` と `uv run scripts\verify_tracked_markdown_links.py` を実行します。
6. 公開対象にする場合は、ルート README と VitePress docs のケース一覧へ追加します。

未完成の試作ケースや参照画像セットは、tracked 公開ケースとして扱う前に上記の検証を通してください。

## 言語方針

ルート README と VitePress docs は英語・日本語を並行して保守します。ケース固有 README や詳細ログは、作成時の作業言語を保持して構いません。その場合でも、ルート README と docs のケース一覧には英語・日本語の概要を揃えて載せます。
