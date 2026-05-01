# Setup and Usage Runbook

This runbook is for `cases\kitchen-trash-cupboard-concept1`. The original `cases\kitchen-trash-cupboard` folder is a reference only.

## Prerequisites

- Windows PowerShell
- `uv` with Python 3.11
- Node.js and npm
- Local OpenSCAD, either installed by this case or supplied with `OPENSCAD_BIN`
- Chrome or Edge for ForgeCAD render attempts

Check the main tools:

```powershell
cd <repo-root>
uv --version
node --version
npm --version
```

## Initial Setup

```powershell
cd <repo-root>
uv sync --python 3.11
cd cases\kitchen-trash-cupboard-concept1
npm install
```

Install or refresh the portable OpenSCAD copy:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_openscad.ps1
```

Check OpenSCAD:

```powershell
tools\OpenSCAD-2021.01-x86-64\openscad-2021.01\openscad.exe --version
```

To use another OpenSCAD binary:

```powershell
$env:OPENSCAD_BIN = "C:\Path\To\openscad.exe"
uv run scripts\generate_openscad.py
```

## Full Generation

Run everything:

```powershell
uv run scripts\run_all.py
```

The full runner executes:

1. CadQuery generation
2. build123d generation
3. OpenSCAD generation
4. JSCAD source generation
5. JSCAD STL/OBJ export
6. JSCAD manifest finalization
7. ForgeCAD source generation
8. ForgeCAD STL/3MF/OBJ/preview generation
9. screenshot collection
10. npm audit collection
11. benchmark scoring
12. STEP import verification
13. OpenSCAD STEP probe
14. text encoding verification
15. report image verification
16. Markdown link verification

The final status is written to [../reports/run_all_last_result.csv](../reports/run_all_last_result.csv).

## Individual Commands

CadQuery:

```powershell
uv run scripts\generate_cadquery.py
```

build123d:

```powershell
uv run scripts\generate_build123d.py
```

OpenSCAD:

```powershell
uv run scripts\generate_openscad.py
```

JSCAD:

```powershell
uv run scripts\generate_jscad_source.py
npm run generate:jscad
uv run scripts\finalize_jscad.py
```

ForgeCAD:

```powershell
uv run scripts\generate_forgecad_source.py
uv run scripts\generate_forgecad.py
```

Report and verification steps:

```powershell
uv run scripts\collect_screenshots.py
uv run scripts\collect_npm_audit.py
uv run scripts\score_outputs.py
uv run scripts\verify_step_imports.py
uv run scripts\verify_openscad_step_probe.py
uv run scripts\verify_text_encoding.py
uv run scripts\verify_report_images.py
uv run scripts\verify_markdown_links.py
```

## Key Artifacts

- [../reports/benchmark_report.md](../reports/benchmark_report.md): benchmark result and screenshots
- [../reports/measurements.csv](../reports/measurements.csv): score totals, category totals, bbox, volume, and watertight checks
- [../reports/score_breakdown.csv](../reports/score_breakdown.csv): four-category score breakdown per tool
- [../reports/score_items.csv](../reports/score_items.csv): itemized scoring evidence and penalties
- [../reports/output_file_fingerprints.csv](../reports/output_file_fingerprints.csv): output file size, mtime, hash, and freshness flag
- [../reports/image_metrics.csv](../reports/image_metrics.csv): screenshot/comparison nonblank, nonwhite, edge-density, and color-sample metrics
- [../reports/non_scored_limits.csv](../reports/non_scored_limits.csv): important limits that are not part of the numeric score
- [../reports/screenshot_inventory.csv](../reports/screenshot_inventory.csv): screenshot collection status
- [../reports/step_imports.csv](../reports/step_imports.csv): CadQuery/build123d STEP import checks
- [../reports/openscad_step_probe.csv](../reports/openscad_step_probe.csv): OpenSCAD STEP probe result
- [../reports/report_image_check.csv](../reports/report_image_check.csv): report image verification
- [../reports/markdown_link_check.csv](../reports/markdown_link_check.csv): Markdown link verification
- [../reports/npm_audit_summary.csv](../reports/npm_audit_summary.csv): npm audit summary

CAD output folders:

- `../outputs/cadquery/`
- `../outputs/build123d/`
- `../outputs/jscad/`
- `../outputs/openscad/`
- `../outputs/forgecad/`

## Current Tool Limits

- CadQuery and build123d export STEP, STL, OBJ, and PNG preview assets.
- JSCAD exports STL and OBJ in this local CLI setup. STEP is not part of the local JSCAD path.
- OpenSCAD 2021.01 exports STL, OBJ via trimesh conversion, and PNG. Its STEP probe currently records `not_generated`.
- ForgeCAD exports STL, 3MF, OBJ via trimesh conversion, and a shared preview PNG. Its STEP probe reports a Pro license requirement.
- ForgeCAD `render 3d` timed out here; the script logs that failure and keeps the reproducible shared preview for reports.
- `npm audit` currently reports four moderate issues. This runbook does not run `npm audit fix` because it can change dependency behavior.

## Completion Checklist

Treat the case as regenerated when all of these are true:

- `uv run scripts\run_all.py` exits with code 0.
- [../reports/run_all_last_result.csv](../reports/run_all_last_result.csv) has `status=ok`.
- [../reports/measurements.csv](../reports/measurements.csv) has rows for all five tools.
- [../reports/score_items.csv](../reports/score_items.csv) shows points, max points, status, and evidence for every scoring item.
- [../reports/output_file_fingerprints.csv](../reports/output_file_fingerprints.csv) records hashes and freshness flags for generated outputs.
- [../reports/image_metrics.csv](../reports/image_metrics.csv) records per-method image metrics for screenshots and concept comparison images.
- [../reports/screenshot_inventory.csv](../reports/screenshot_inventory.csv) has `status=ok` for all five tools.
- [../reports/report_image_check.csv](../reports/report_image_check.csv) reports nonblank PNGs.
- [../reports/markdown_link_check.csv](../reports/markdown_link_check.csv) has no broken relative links.
- [../reports/encoding_check.csv](../reports/encoding_check.csv) does not report text encoding failures for the case docs.

Current itemized score totals are CadQuery `84.0` / B, build123d `84.0` / B, JSCAD `76.0` / C, OpenSCAD `76.0` / C, and ForgeCAD `76.0` / C.
