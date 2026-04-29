# 無料CAD生成候補の棚卸し（2026-04-29時点）

## 判定

| 候補 | 無料ローカル実行 | 今回の扱い | 理由 |
|---|---:|---|---|
| text-to-cad | OK | 参考上位 | GitHub上では Codex/Claude Code 等のエージェント向けローカルCADハーネス。build123d/OCP、STEP/STL/DXF/GLB、ローカルviewerを掲げている。今回の実生成は同系統の build123d/CadQuery を直接ベンチ。 |
| CadQuery | OK | 実行 | Python CAD-as-code。STEP/STL/OBJ/PNGを生成。 |
| build123d | OK | 実行 | Python CAD-as-code。STEP/STL/OBJ/PNGを生成。text-to-cad系の実用エンジンとして近い。 |
| JSCAD/OpenJSCAD | OK | 実行 | Node.js CLIでSTL/OBJ生成。STEPなし。 |
| OpenSCAD | OK | 実行 | 公式zipをワークスペース内にポータブル配置済み。SCAD/STL/PNGをOpenSCAD CLIで生成し、OBJはSTLから変換。OpenSCAD 2021.01のこの実行手順ではSTEPは未生成。 |
| ForgeCAD CLI | OK（非本番利用） | 実行 | npm package `forgecad@0.8.2`。BUSL-1.1で非本番利用は無料。`run`/`render 3d`/`export stl`/`export 3mf` は実行可能、STEP export はProライセンス要求で未生成。 |
| CADAM | APIキー前提 | 参考 | OSSだがローカルAI生成には `ANTHROPIC_API_KEY`、Supabase、ngrok等が必要。無料ローカル完結とは言いにくい。 |
| OpenSCAD Studio / ModelRift系 | 条件付き | 参考 | OpenSCAD編集/プレビュー環境として有用。AI機能は外部モデル/API設定が絡みやすい。 |
| Fusion 360 / Onshape MCP系 | NG | 今回除外 | 外部CADアプリ、アカウント、利用条件、MCPブリッジが必要。無料枠があってもローカルOSSベンチではない。 |

## 参照した一次情報

- text-to-cad: <https://github.com/earthtojake/text-to-cad>  
  GitHub READMEで、Codex/Claude Code等での生成、STEP/STL/DXF/GLB出力、ローカルCAD Explorer、ローカル実行が明記されている。
- CADAM: <https://github.com/Adam-CAD/CADAM>  
  OpenSCAD WASM、Three.js、Anthropic Claude API、Supabase構成がREADMEに明記されている。
- OpenSCAD Studio: <https://github.com/zacharyfmarion/openscad-studio>  
  OpenSCAD向けのライブプレビュー、診断、AI copilot、多ファイルワークフローを掲げる。
- JSCAD/OpenJSCAD: <https://github.com/jscad/OpenJSCAD.org>  
  Web/セルフホスト/CLIで使えるJavaScriptベースのオープンソースCAD。
- build123d: <https://build123d.readthedocs.io/en/latest/>  
  OpenCascadeベースのPythonパラメトリックBREP CAD。
- CadQuery: <https://cadquery.readthedocs.io/en/latest/>  
  Pythonで記述するパラメトリックCAD。STEPなどの高品質CAD形式出力を目的に含む。
- ForgeCAD: <https://github.com/KoStard/ForgeCAD>  
  READMEで `npm install -g forgecad`、CLIの `run`/`render`/`export` ワークフロー、BUSL-1.1ライセンスが案内されている。

## 未確認

- X（旧Twitter）の投稿URL、いいね数、閲覧数はこのベンチ中に一次確認していません。貼られた数値は参考情報に留めています。
- CADAMのWeb版無料クレジット残量や、Fusion 360/Onshapeの現在の利用条件は日々変わるため、今回の実行ベンチには入れていません。
