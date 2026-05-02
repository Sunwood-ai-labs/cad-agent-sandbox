<p align="center">
  <img src="docs/public/cad-agent-sandbox.svg" alt="CAD Agent Sandbox ロゴ" width="112">
</p>

<h1 align="center">CAD Agent Sandbox</h1>

<p align="center">
  ローカルで無料実行できる CAD-as-code ツールを、同じ家具仕様で比較するための Windows 前提ベンチマーク作業場です。
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="https://sunwood-ai-labs.github.io/cad-agent-sandbox/ja/">公開 docs</a> | <a href="docs/ja/index.md">docs ソース</a>
</p>

<p align="center">
  <a href="https://github.com/Sunwood-ai-labs/cad-agent-sandbox/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Sunwood-ai-labs/cad-agent-sandbox/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/Sunwood-ai-labs/cad-agent-sandbox/actions/workflows/pages.yml"><img alt="Docs" src="https://github.com/Sunwood-ai-labs/cad-agent-sandbox/actions/workflows/pages.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-2563eb.svg"></a>
  <img alt="Python 3.11" src="https://img.shields.io/badge/Python-3.11-0f766e.svg">
  <img alt="Windows first" src="https://img.shields.io/badge/Windows-first-7c3aed.svg">
</p>

## 🚪 これは何か

CAD Agent Sandbox は、反復可能な CAD-as-code ベンチマークケースを `cases/` にまとめるリポジトリです。各ケースは同じ家具仕様を複数のローカルツールチェーンで生成し、軽量な証跡を残し、再生成できる CAD 成果物は Git の外に置きます。

比較対象は主に次の観点です。

- CadQuery / build123d などの Python CAD スタック
- JSCAD / OpenSCAD / ForgeCAD CLI などの JavaScript・テキストベースのスタック
- STEP / STL / OBJ / PNG の出力対応と再現性
- スクリーンショット、レポート、HyperFrames 動画ソースの運用

## ⚡ 最短実行

```powershell
cd <repo-root>
uv sync --python 3.11
cd cases\cupboard
npm install
powershell -ExecutionPolicy Bypass -File scripts\install_openscad.ps1
uv run scripts\run_all.py
```

別ケースを試す場合は `cases\kitchen-trash-cupboard` または `cases\kitchen-trash-cupboard-concept1` に移動します。

## 🗂️ ケース

| ケース | 焦点 | レポート | 動画ソース |
|---|---|---|---|
| [cupboard](cases/cupboard/) | 幅 900 x 奥行 450 x 高さ 2000 mm の基本カップボード | [benchmark report](cases/cupboard/reports/benchmark_report.md) | [HyperFrames source](cases/cupboard/videos/cupboard-cad-comparison/) |
| [kitchen-trash-cupboard](cases/kitchen-trash-cupboard/) | 幅 1680 x 奥行 650 x 高さ 1800 mm、下部にゴミ箱 3 台を置けるキッチンカップボード | [benchmark report](cases/kitchen-trash-cupboard/reports/benchmark_report.md) | [HyperFrames source](cases/kitchen-trash-cupboard/videos/kitchen-trash-cupboard-comparison/) |
| [kitchen-trash-cupboard-concept1](cases/kitchen-trash-cupboard-concept1/) | コンセプト画像に寄せた詳細採点付きバリアント | [benchmark report](cases/kitchen-trash-cupboard-concept1/reports/benchmark_report.md) | [HyperFrames source](cases/kitchen-trash-cupboard-concept1/videos/kitchen-trash-cupboard-concept1-comparison/) |

## 🧰 ツールチェーン

| ツールチェーン | 入力 | 主な出力 | メモ |
|---|---|---|---|
| CadQuery | Python | STEP / STL / OBJ / PNG | OpenCascade/OCP 系で再編集しやすい CAD 出力が強い |
| build123d | Python | STEP / STL / OBJ / PNG | Python-first のモデリングで STEP 出力が安定 |
| JSCAD | JavaScript | STL / OBJ / PNG | 軽量なローカル生成経路 |
| OpenSCAD | `.scad` | SCAD / STL / OBJ / PNG | ケースごとに Windows 用ポータブル CLI を導入 |
| ForgeCAD CLI | JavaScript | STL / 3MF / OBJ / PNG | 現在の無料ローカル経路では STEP を出力しない |

## 📚 ドキュメント

- [docs ホーム](docs/ja/index.md)
- [はじめかた](docs/ja/guide/getting-started.md)
- [ケースガイド](docs/ja/guide/cases.md)
- [検証ガイド](docs/ja/guide/verification.md)
- [ケース構成ルール](docs/CASE_LAYOUT.md)

公開ドキュメントは VitePress でビルドし、`.github/workflows/pages.yml` から GitHub Pages へデプロイします。

## 🧪 検証

ルートから軽量チェックを実行できます。

```powershell
uv run cases\cupboard\scripts\verify_text_encoding.py
uv run scripts\verify_tracked_markdown_links.py
npm run docs:build
```

CAD まで再生成する場合は、対象ケースの Node 依存と OpenSCAD を入れたうえで、ケースディレクトリ内から `uv run scripts\run_all.py` を実行します。

## 🧭 リポジトリ構成

```text
cases/<slug>/
  README.md
  docs/
  cupboard_benchmark/      # ケース仕様と共通ヘルパー
  designs/                 # OpenSCAD / JSCAD / ForgeCAD ソース
  outputs/                 # 再生成される CAD 成果物。Git では追跡しない
  reports/                 # 公開用の軽量レポートとスクリーンショット
  scripts/                 # 生成と検証の再現用スクリプト
  videos/                  # HyperFrames 動画ソースと素材
```

生成済み CAD、レンダー済み MP4、QA フレーム、ローカルツール、依存ディレクトリ、内部ログは再生成可能なため追跡しません。

## ⚠️ 制約

これは CAD 生成・可視化・出力形式のベンチマークです。家具としての強度、転倒、耐荷重、壁固定、安全規格、製造適格性のサインオフではありません。

一部ツールチェーンの制約はレポートに明記しています。たとえば現在の無料ローカル ForgeCAD 経路と OpenSCAD 2021.01 経路では STEP は未生成です。

## 📄 ライセンス

コードとドキュメントは [MIT License](LICENSE) で公開します。
