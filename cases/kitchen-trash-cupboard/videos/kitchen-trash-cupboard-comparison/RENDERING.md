# Kitchen Trash Cupboard Comparison Video Rendering

このファイルは、`kitchen-trash-cupboard-comparison` HyperFrames 動画をレンダーした証跡と再実行手順です。

## 参照した構成

- 参照動画プロジェクト: `cases\cupboard\videos\cupboard-cad-comparison`
- 対象動画プロジェクト: `cases\kitchen-trash-cupboard\videos\kitchen-trash-cupboard-comparison`
- どちらも `DESIGN.md` の botanical theme、82秒構成、9シーン比較、常設フッターを踏襲します。

## レンダー手順

```powershell
cd <repo-root>\cases\kitchen-trash-cupboard\videos\kitchen-trash-cupboard-comparison
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect --samples 12
npx hyperframes render --output renders\kitchen-trash-cupboard-comparison.mp4 --quality standard --fps 30
```

## 2026-05-01 の確認済みローカル成果物

- MP4: `renders\kitchen-trash-cupboard-comparison.mp4`
- Duration: `82.000000` seconds
- Size: `7511192` bytes
- SHA256: `A5227BDB3578E214D1A20F6FA4C1EEE19B825540F153A3DC71565D9F1DE09779`
- Render settings: `standard`, `30fps`, `1920x1080`

## QA フレーム

参照側の `qa_frames` と同じ目的で、対象側にも下記を生成します。これらは再生成可能なため Git 追跡外です。

```powershell
ffmpeg -y -ss 0 -i renders\kitchen-trash-cupboard-comparison.mp4 -frames:v 1 qa_frames\audit_first_frame.png
ffmpeg -y -i renders\kitchen-trash-cupboard-comparison.mp4 -vf "fps=1/8.2,scale=384:-1,tile=5x2" -frames:v 1 -update 1 qa_frames\contact_sheet.png
ffmpeg -y -i renders\kitchen-trash-cupboard-comparison.mp4 -vf "select='eq(n,0)+eq(n,240)+eq(n,510)+eq(n,810)+eq(n,1080)+eq(n,1350)+eq(n,1620)+eq(n,1890)+eq(n,2160)',scale=384:-1,tile=3x3" -frames:v 1 -update 1 qa_frames\scene_start_sheet.png
ffmpeg -y -i renders\kitchen-trash-cupboard-comparison.mp4 -vf "select='eq(n,234)+eq(n,246)+eq(n,504)+eq(n,516)+eq(n,804)+eq(n,816)+eq(n,1074)+eq(n,1086)+eq(n,1344)+eq(n,1356)+eq(n,1614)+eq(n,1626)+eq(n,1884)+eq(n,1896)+eq(n,2154)+eq(n,2166)',scale=320:-1,tile=4x4" -frames:v 1 -update 1 qa_frames\transition_boundary_sheet.png
```

## Git 追跡ポリシー

`renders\` と `qa_frames\` は生成物なので公開リポジトリでは追跡しません。追跡対象は、動画ソース、素材、デザイン指針、再現手順、軽量な証跡のみです。
