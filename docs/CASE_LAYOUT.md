# Case Layout

このリポジトリは、別テーマのCADベンチマークを `cases/<slug>/` として追加できる構成にしています。

公開で追跡するもの:

- ケース固有の README / docs / scripts / CAD ソース
- 軽量な比較レポート CSV / Markdown
- レポート用スクリーンショット
- HyperFrames の動画ソースと素材

追跡しないもの:

- `cases/*/outputs/`
- `cases/*/reports/encoding_check.csv` などの再生成ログ
- `cases/*/reports/video_views/`
- `cases/*/videos/*/renders/`
- `cases/*/videos/*/qa_frames/`
- `cases/*/videos/*/.hyperframes/`
- `cases/*/tools/`
- `cases/*/node_modules/`

現在のケース:

- [cases/cupboard/](../cases/cupboard/): 基本カップボード
- [cases/kitchen-trash-cupboard/](../cases/kitchen-trash-cupboard/): ゴミ箱3台対応キッチンカップボード

新しいケースを追加する時は、まず既存ケースを複製し、README と docs のテーマ名、仕様、出力先、動画タイトルを更新します。`videos/<slug>-comparison/` の slug もケース固有にしておくと、公開導線が混ざりにくくなります。
