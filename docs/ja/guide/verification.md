# 検証

ドキュメントやレポート変更の前後では軽量チェックを使います。ケースのソースや採点ロジックを変えた場合だけ、CAD まで含む full regeneration を実行します。

## ドキュメント確認

```powershell
cd D:\Prj\cad-agent-sandbox
uv run cases\cupboard\scripts\verify_text_encoding.py
uv run scripts\verify_tracked_markdown_links.py
npm run docs:build
```

文字化け確認は `.venv`、`node_modules`、`tools` を除く Markdown / HTML を見ます。tracked リンク確認は、ローカルの未追跡実験ケースを除外しつつ、tracked docs とルート README を確認します。

## ケース確認

ケースディレクトリから実行します。

```powershell
uv run scripts\verify_step_imports.py
uv run scripts\verify_openscad_step_probe.py
uv run scripts\verify_report_images.py
uv run scripts\verify_markdown_links.py
```

ソース生成、スクリーンショット、採点、レポートをまとめて更新する場合は `uv run scripts\run_all.py` を使います。

## コミット前の payload 確認

コミット前に staged payload を確認し、大きな再生成物を除外します。

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_commit_payload.ps1 -RepoPath .
```

`node_modules`、`.venv`、`tools`、`outputs`、動画レンダー、QA フレームはコミットに含めません。
