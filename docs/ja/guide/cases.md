# ケース

各 tracked ケースは `cases/<slug>/` 配下の自己完結したベンチマーク作業場です。

## ケース一覧

| ケース | モデル | 主な証跡 | メモ |
|---|---|---|---|
| [cupboard](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/cupboard) | 幅 900 x 奥行 450 x 高さ 2000 mm の基本カップボード | [レポート](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/blob/main/cases/cupboard/reports/benchmark_report.md) | 共有ワークフローのベースライン |
| [kitchen-trash-cupboard](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard) | 幅 1680 x 奥行 650 x 高さ 1800 mm、ゴミ箱 3 台対応 | [レポート](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/blob/main/cases/kitchen-trash-cupboard/reports/benchmark_report.md) | 実用寄りのキッチン収納ベンチマーク |
| [kitchen-trash-cupboard-concept1](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard-concept1) | コンセプト画像に合わせたキッチンカップボード派生ケース | [レポート](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/blob/main/cases/kitchen-trash-cupboard-concept1/reports/benchmark_report.md) | コンセプト比較と視覚採点の証跡を含む |

## ケースに含めるもの

```text
cases/<slug>/
  README.md
  docs/
  cupboard_benchmark/
  designs/
  outputs/
  reports/
  scripts/
  videos/
```

ケース README には、モデル、ツールチェーン、セットアップ手順、出力、検証状態、スクリーンショット、既知の制約をまとめます。

## Git に入れないもの

生成 CAD、ローカル OpenSCAD、依存ディレクトリ、レンダー済み MP4、QA フレーム、内部ログは、小さな公開証跡として意図的に残す場合を除いて Git の外に置きます。

追跡ルールは [ケース構成](../../CASE_LAYOUT.md) にまとめています。
