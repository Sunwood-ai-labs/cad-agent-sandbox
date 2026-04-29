# Setup and Usage Runbook

このメモは、次回以降に `cases\cupboard` でカップボード CAD ベンチを再開するための手順書です。Windows + PowerShell + `uv` 前提で書いています。

## 1. 前提ツール

必要なもの:

- PowerShell
- Python 3.11 を `uv` から使えること。`pyproject.toml` の制約は `>=3.11,<3.12` です
- Node.js / npm。`npm install` で `@jscad/cli`、`@jscad/modeling`、`forgecad` を入れます
- 初回だけインターネット接続
- ForgeCAD の PNG render 用に Google Chrome または Microsoft Edge があると安定します

確認コマンド:

```powershell
cd <repo-root>
uv --version
node --version
npm --version
```

## 2. 初回セットアップ

Python 依存を入れます。

```powershell
cd <repo-root>
uv sync --python 3.11
cd cases\cupboard
```

Node 依存を入れます。

```powershell
npm install
```

OpenSCAD をケース内にポータブル配置します。

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_openscad.ps1
```

OpenSCAD の導入確認:

```powershell
tools\OpenSCAD-2021.01-x86-64\openscad-2021.01\openscad.exe --version
```

期待値:

```text
OpenSCAD version 2021.01
```

別の OpenSCAD を使う場合:

```powershell
$env:OPENSCAD_BIN = "C:\Path\To\openscad.exe"
uv run scripts/generate_openscad.py
```

`OPENSCAD_BIN` が未設定の場合、スクリプトは `PATH` 上の `openscad`、次にケース内の `tools\OpenSCAD-2021.01-x86-64\openscad-2021.01\openscad.exe` を探します。

## 3. 一括ベンチ実行

通常はこれだけで十分です。

```powershell
uv run scripts/run_all.py
```

この一括スクリプトは、次を順番に実行します。

1. CadQuery 生成
2. build123d 生成
3. OpenSCAD 生成
4. JSCAD ソース生成
5. JSCAD CLI で STL/OBJ 生成
6. JSCAD 後処理
7. ForgeCAD ソース生成
8. ForgeCAD CLI で STL/3MF/PNG 生成
9. スクリーンショット集約
10. npm audit 要約
11. 採点レポート生成
12. STEP import 検証
13. OpenSCAD STEP probe
14. 文字コード検証
15. レポート画像検証
16. Markdown リンク検証

最後に `reports\run_all_last_result.csv` へ、実行日時、成功/失敗、戻り値、完了ステップ数を書きます。

## 4. 個別コマンド

CadQuery:

```powershell
uv run scripts/generate_cadquery.py
```

build123d:

```powershell
uv run scripts/generate_build123d.py
```

OpenSCAD:

```powershell
uv run scripts/generate_openscad.py
```

JSCAD:

```powershell
uv run scripts/generate_jscad_source.py
npm run generate:jscad
uv run scripts/finalize_jscad.py
```

ForgeCAD:

```powershell
uv run scripts/generate_forgecad_source.py
uv run scripts/generate_forgecad.py
```

レポート更新:

```powershell
uv run scripts/collect_screenshots.py
uv run scripts/collect_npm_audit.py
uv run scripts/score_outputs.py
uv run scripts/verify_step_imports.py
uv run scripts/verify_openscad_step_probe.py
uv run scripts/verify_text_encoding.py
uv run scripts/verify_report_images.py
uv run scripts/verify_markdown_links.py
```

## 5. 成果物

主要レポート:

- [reports/benchmark_report.md](../reports/benchmark_report.md): 採点表、ツール比較、スクリーンショット、既知リスク
- [reports/measurements.csv](../reports/measurements.csv): 採点の元データ
- `reports/run_all_last_result.csv`: 一括実行の最終結果（再生成されます）
- [reports/tool_landscape.md](../reports/tool_landscape.md): 実行対象と参考候補の棚卸し
- [reports/step_imports.csv](../reports/step_imports.csv): CadQuery/build123d STEP import 検証
- [reports/openscad_step_probe.csv](../reports/openscad_step_probe.csv): OpenSCAD STEP 生成可否の probe
- `reports/report_image_check.csv`: Markdown 画像リンクと PNG の非空チェック（再生成されます）
- `reports/markdown_link_check.csv`: README/レポート内の相対リンク検証（再生成されます）
- [reports/npm_audit_summary.csv](../reports/npm_audit_summary.csv): npm audit の件数要約

スクリーンショット:

- [reports/screenshots/cadquery.png](../reports/screenshots/cadquery.png)
- [reports/screenshots/build123d.png](../reports/screenshots/build123d.png)
- [reports/screenshots/jscad.png](../reports/screenshots/jscad.png)
- [reports/screenshots/openscad.png](../reports/screenshots/openscad.png)
- [reports/screenshots/forgecad.png](../reports/screenshots/forgecad.png)

ツール別出力:

- `outputs/cadquery/`
- `outputs/build123d/`
- `outputs/jscad/`
- `outputs/openscad/`
- `outputs/forgecad/`

`outputs/` は再生成できるCAD成果物置き場です。公開リポジトリでは追跡せず、`uv run scripts/run_all.py` の実行後にローカルへ作成されます。

## 6. スコアの見方

`reports\benchmark_report.md` の主な列:

- `Source`: ソースコードや設計ファイルが生成されたか
- `STEP`: ネイティブ CAD 再編集に向く STEP が生成されたか
- `STL` / `OBJ`: メッシュ出力が生成されたか
- `PNG`: レポート用画像が生成されたか
- `bbox`: 期待 bbox との差が ±1mm 以内か
- `volume`: 期待体積との差が 2% 以内か
- `watertight`: STL/OBJ が閉じたメッシュとして読めるか

現状の重要な差:

- CadQuery / build123d は STEP が出るため、再編集性で有利です。
- JSCAD / OpenSCAD は軽く扱えますが、この構成では STEP なしです。
- ForgeCAD は CLI 体験がよく STL/3MF/PNG は出ますが、無料ローカルでは STEP が Pro ライセンス要求です。現状の STL/OBJ は bbox/volume は合格、watertight は NG です。

## 7. 仕様変更したいとき

寸法や部品構成を変える場合は、まず `cupboard_benchmark\spec.py` を変更します。

その後、全体を再生成します。

```powershell
uv run scripts/run_all.py
```

変更後に必ず見るもの:

- `reports\measurements.csv`
- `reports\benchmark_report.md`
- `reports\report_image_check.csv`
- `reports\screenshots\*.png`

## 8. 新しいCAD手法を追加するとき

追加時の最小チェックリスト:

1. 共通仕様は `cupboard_benchmark\spec.py` から読む
2. 新規生成スクリプトを `scripts\generate_<method>.py` か npm script として追加
3. 出力先は `outputs\<method>\` に統一
4. 可能なら source / STEP / STL / OBJ / PNG / manifest を出す
5. `scripts\collect_screenshots.py` にスクリーンショット収集を追加
6. `scripts\score_outputs.py` の候補一覧と採点メモを更新
7. `scripts\run_all.py` に実行順を追加
8. `uv run scripts/run_all.py` で全体検証
9. README と `reports\tool_landscape.md` に制約を追記

## 9. トラブルシュート

### PowerShell 上で日本語が文字化けする

表示だけの問題か、ファイル自体の問題かを分けます。

```powershell
uv run scripts/verify_text_encoding.py
```

`mojibake_marker_count=0` なら、少なくとも検査対象ファイルは UTF-8 として読めています。

検査対象は `.venv` / `node_modules` / `tools` を除くワークスペース内 Markdown / HTML です。

### OpenSCAD が見つからない

まずインストールスクリプトを再実行します。

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_openscad.ps1
```

その後、バージョンを確認します。

```powershell
tools\OpenSCAD-2021.01-x86-64\openscad-2021.01\openscad.exe --version
```

### ForgeCAD の STEP が出ない

現状の無料ローカル実行では、ForgeCAD CLI が `export step requires a ForgeCAD Pro license` を返します。これは失敗を隠さず、`outputs\forgecad\forgecad_step_probe.txt` と `reports\benchmark_report.md` に残す方針です。

無料枠で比較する場合は STL / 3MF / PNG / OBJ までを評価対象にします。

### npm audit で moderate が出る

要約は一括実行で自動的に保存されます。

```powershell
uv run scripts/collect_npm_audit.py
```

`npm audit fix` は依存バージョンや出力挙動が変わる可能性があるため、明示依頼なしには実行しません。

### 画像リンクが壊れていないか確認したい

```powershell
uv run scripts/verify_report_images.py
```

結果は `reports\report_image_check.csv` に出ます。`status=ok` かつ `nonblank=True` を確認します。

### Markdownリンクが壊れていないか確認したい

```powershell
uv run scripts/verify_markdown_links.py
```

結果は `reports\markdown_link_check.csv` に出ます。相対リンクは `status=ok`、外部リンクは `status=external` になります。

検査対象は `.venv` / `node_modules` / `tools` を除くワークスペース内 Markdown です。

## 10. 完了判定

次が満たせていれば、今回のベンチ成果物は再生成済みとして扱えます。

- `uv run scripts/run_all.py` が exit code 0
- `reports\run_all_last_result.csv` が `status=ok` / `returncode=0`
- `reports\benchmark_report.md` が更新済み
- `reports\measurements.csv` に各方法の行がある
- `reports\report_image_check.csv` が全画像 `ok` / `nonblank=True`
- `reports\markdown_link_check.csv` が相対リンク `ok`
- `reports\encoding_check.csv` で README / report 系が UTF-8 として読める
- 失敗や制約が `未確認` ではなく、レポート上のメモや probe ログに残っている
