# CAD Agent Sandbox

無料でローカル実行できる CAD-as-code 系ツールを、テーマ別の `cases/` に分けて比較するための作業リポジトリです。

現在の公開ケースはカップボードです。

- ケース本体: [cases/cupboard/](cases/cupboard/)
- セットアップと使い方: [cases/cupboard/docs/SETUP_AND_USAGE.md](cases/cupboard/docs/SETUP_AND_USAGE.md)
- ベンチマークレポート: [cases/cupboard/reports/benchmark_report.md](cases/cupboard/reports/benchmark_report.md)
- 比較動画ソース: [cases/cupboard/videos/cupboard-cad-comparison/](cases/cupboard/videos/cupboard-cad-comparison/)

## ケース構成

各テーマは `cases/<slug>/` にまとめます。

```text
cases/<slug>/
  README.md
  docs/
  cupboard_benchmark/      # そのケースの仕様と共通ヘルパー
  designs/                 # OpenSCAD / JSCAD / ForgeCAD などのCADソース
  outputs/                 # 再生成されるCAD成果物。Gitでは追跡しない
  reports/                 # 公開用の軽量レポートとスクリーンショット
  scripts/                 # そのケースを再生成する実行スクリプト
  videos/                  # HyperFrames動画ソースと素材
```

生成済み CAD、レンダー済み MP4、QA フレーム、ローカルツール、依存ディレクトリは再生成可能なため追跡しません。

## 最短実行

```powershell
cd <repo-root>
uv sync --python 3.11
cd cases\cupboard
npm install
powershell -ExecutionPolicy Bypass -File scripts\install_openscad.ps1
uv run scripts\run_all.py
```

詳細な運用ルールは [docs/CASE_LAYOUT.md](docs/CASE_LAYOUT.md) にもまとめています。
