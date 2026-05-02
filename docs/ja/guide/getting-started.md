# はじめかた

このページでは、tracked ケースの `cupboard` を使って最短ルートを説明します。

## 必要なもの

- Windows と PowerShell
- `uv` で管理する Python
- JSCAD、ForgeCAD CLI、docs 用の Node.js / npm
- clone と差分確認用の Git

## 1. Python 依存を同期する

```powershell
cd <repo-root>
uv sync --python 3.11
```

ルートの `pyproject.toml` は Python 範囲を `>=3.11,<3.12` に固定しています。

## 2. ケースの Node 依存を入れる

```powershell
cd cases\cupboard
npm install
```

Node 側の CAD 依存はケースごとの `package.json` で管理します。

## 3. ポータブル OpenSCAD を入れる

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_openscad.ps1
```

OpenSCAD はケース内の `tools\` に配置されます。このディレクトリは再生成できるため Git では追跡しません。

## 4. ベンチマークを実行する

```powershell
uv run scripts\run_all.py
```

正常終了すると軽量レポートとスクリーンショットが更新されます。`outputs\` 配下の CAD ファイルは ignored のままです。

## 5. docs をビルドする

```powershell
cd <repo-root>
npm install
npm run docs:build
```

ルートの npm scripts は `docs/` 配下の VitePress プロジェクトへ処理を委譲します。

## 次に見るもの

- 別のベンチマークを選ぶ場合は [ケース](./cases.md) を確認します。
- ドキュメントやレポートを公開前に確認する場合は [検証](./verification.md) を確認します。
