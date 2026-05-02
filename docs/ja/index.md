---
layout: home

hero:
  name: CAD Agent Sandbox
  text: ローカル CAD-as-code ベンチマーク集。
  tagline: 同じ家具仕様から CadQuery、build123d、JSCAD、OpenSCAD、ForgeCAD CLI を比較します。
  image:
    src: /cad-agent-sandbox.svg
    alt: CAD Agent Sandbox
  actions:
    - theme: brand
      text: はじめる
      link: /ja/guide/getting-started
    - theme: alt
      text: ケースを見る
      link: /ja/guide/cases

features:
  - title: Windows 前提
    details: PowerShell、uv、npm、ポータブル OpenSCAD を使う実際のケースに合わせた手順です。
  - title: 再現できる証跡
    details: ソース、レポート、スクリーンショット、動画ソースを残し、再生成できる CAD 成果物は除外します。
  - title: 日英ドキュメント
    details: 英語と日本語のガイドを同じ構成にして、同じ作業手順を追えるようにします。
---

## 現在のケース

| ケース | 焦点 | 入口 |
|---|---|---|
| `cupboard` | 基本カップボードのベンチマーク | [ケースを開く](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/cupboard) |
| `kitchen-trash-cupboard` | ゴミ箱 3 台対応キッチンカップボード | [ケースを開く](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard) |
| `kitchen-trash-cupboard-concept1` | コンセプト画像に寄せた派生ケース | [ケースを開く](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard-concept1) |

まず [はじめかた](./guide/getting-started.md) を確認し、次に [ケースガイド](./guide/cases.md) から対象ケースを選びます。
