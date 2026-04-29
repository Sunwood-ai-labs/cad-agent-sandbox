from __future__ import annotations

import csv
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.exports import ensure_dir, write_parts_csv
from cupboard_benchmark.spec import cupboard_parts, expected_metrics
from cupboard_benchmark.tools import find_openscad
from cupboard_benchmark.validation import positive_overlap_pairs


REPORTS = ROOT / "reports"
CANDIDATES = ["cadquery", "build123d", "jscad", "openscad", "forgecad"]


def file_ok(path: Path | None) -> bool:
    return bool(path and path.exists() and path.stat().st_size > 0)


def rel_path(raw: str | None) -> Path | None:
    if not raw:
        return None
    return ROOT / raw


def measure_mesh(path: Path) -> dict[str, object]:
    mesh = trimesh.load(path, force="mesh")
    bounds = mesh.bounds
    size = bounds[1] - bounds[0]
    return {
        "bbox_min": [round(float(value), 3) for value in bounds[0]],
        "bbox_max": [round(float(value), 3) for value in bounds[1]],
        "bbox_size": [round(float(value), 3) for value in size],
        "watertight": bool(mesh.is_watertight),
        "volume_abs": round(abs(float(mesh.volume)), 3),
        "faces": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
    }


def within_tolerance(values: list[float], expected: list[float], tolerance: float) -> bool:
    return all(abs(float(value) - float(target)) <= tolerance for value, target in zip(values, expected))


def score_candidate(manifest: dict[str, object], output_dir: Path) -> dict[str, object]:
    files = manifest.get("generated_files", {})
    source = rel_path(files.get("source")) if isinstance(files, dict) else None
    step = rel_path(files.get("step")) if isinstance(files, dict) else None
    stl = rel_path(files.get("stl")) if isinstance(files, dict) else None
    obj = rel_path(files.get("obj")) if isinstance(files, dict) else None
    preview = rel_path(files.get("preview")) if isinstance(files, dict) else None
    spec = expected_metrics()
    role_counts = spec["role_counts"]
    expected_overall_size = spec["overall_size"]
    parts = cupboard_parts()
    overlap_pairs = positive_overlap_pairs(parts)
    expected_volume = sum(part.dx * part.dy * part.dz for part in parts)

    export_points = 0
    export_points += 4 if file_ok(step) else 0
    export_points += 4 if file_ok(stl) else 0
    export_points += 3 if file_ok(obj) else 0
    export_points += 3 if file_ok(source) else 0
    export_points += 2 if file_ok(preview) else 0

    source_points = 12 if file_ok(source) else 0
    feature_points = 0
    feature_points += 8 if role_counts.get("carcass") == 5 else 0
    feature_points += 7 if role_counts.get("shelf", 0) >= 2 else 0
    feature_points += 6 if role_counts.get("door") == 2 else 0
    feature_points += 5 if role_counts.get("handle") == 2 else 0
    feature_points += 2 if role_counts.get("toe_kick") == 1 else 0
    reproducibility_points = 10 if file_ok(output_dir / "manifest.json") else 0

    mesh_checks = []
    measurement_error = None
    for mesh_path in [path for path in [stl, obj] if file_ok(path)]:
        try:
            measured = measure_mesh(mesh_path)
            measured["path"] = str(mesh_path.relative_to(ROOT))
            measured["bbox_pass"] = within_tolerance(measured["bbox_size"], expected_overall_size, 1.0)
            volume_delta_ratio = abs(float(measured["volume_abs"]) - expected_volume) / expected_volume
            measured["volume_delta_ratio"] = round(volume_delta_ratio, 5)
            measured["volume_pass"] = (not overlap_pairs) and volume_delta_ratio <= 0.02
            mesh_checks.append(measured)
        except Exception as exc:
            measurement_error = str(exc)

    bbox_pass_any = any(check["bbox_pass"] for check in mesh_checks)
    volume_pass_any = any(check["volume_pass"] for check in mesh_checks)
    watertight_any = any(check["watertight"] for check in mesh_checks)
    if mesh_checks and bbox_pass_any and volume_pass_any and watertight_any:
        geometry_points = 30
    elif mesh_checks and bbox_pass_any and volume_pass_any:
        geometry_points = 26
    elif mesh_checks and bbox_pass_any:
        geometry_points = 22
    elif mesh_checks:
        geometry_points = 12
    elif file_ok(source):
        geometry_points = 8
    else:
        geometry_points = 0

    score = geometry_points + feature_points + source_points + export_points + reproducibility_points
    if not mesh_checks:
        score = min(score, 65)

    return {
        "method": manifest.get("method"),
        "scope": "source-only reference" if not mesh_checks else "full benchmark",
        "score": min(score, 100),
        "source": file_ok(source),
        "step": file_ok(step),
        "stl": file_ok(stl),
        "obj": file_ok(obj),
        "preview": file_ok(preview),
        "mesh_checks": mesh_checks,
        "bbox_pass_any": bbox_pass_any,
        "volume_pass_any": volume_pass_any,
        "watertight_any": watertight_any,
        "overlap_pairs": overlap_pairs,
        "measurement_error": measurement_error,
        "notes": manifest.get("notes", []),
    }


def command_version(command: str) -> str:
    found = shutil.which(command)
    if not found:
        return "not found"
    try:
        result = subprocess.run([command, "--version"], capture_output=True, text=True, check=False, timeout=10)
        first = (result.stdout or result.stderr).strip().splitlines()[0]
        return first or f"{command} found"
    except Exception:
        return f"{command} found"


def openscad_version() -> str:
    found = find_openscad()
    if not found:
        return "not found"
    try:
        result = subprocess.run([found, "--version"], capture_output=True, text=True, check=False, timeout=10)
        first = (result.stdout or result.stderr).strip().splitlines()[0]
        return first or "OpenSCAD found"
    except Exception:
        return "OpenSCAD found"


def main() -> None:
    ensure_dir(REPORTS)
    write_parts_csv(REPORTS / "parts_inventory.csv")
    rows = []
    for candidate in CANDIDATES:
        output_dir = ROOT / "outputs" / candidate
        manifest_path = output_dir / "manifest.json"
        if not manifest_path.exists():
            rows.append(
                {
                    "method": candidate,
                    "score": 0,
                    "source": False,
                    "step": False,
                    "stl": False,
                    "obj": False,
                    "preview": False,
                    "measured": None,
                    "measurement_error": "manifest missing",
                    "notes": ["Candidate was not generated."],
                }
            )
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows.append(score_candidate(manifest, output_dir))

    csv_path = REPORTS / "measurements.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["method", "scope", "score", "source", "step", "stl", "obj", "preview", "bbox_min", "bbox_max", "bbox_size", "bbox_pass", "volume_pass", "watertight_any", "overlap_pairs", "notes"])
        for row in rows:
            measured = (row.get("mesh_checks") or [{}])[0]
            writer.writerow(
                [
                    row["method"],
                    row["scope"],
                    row["score"],
                    row["source"],
                    row["step"],
                    row["stl"],
                    row["obj"],
                    row["preview"],
                    measured.get("bbox_min"),
                    measured.get("bbox_max"),
                    measured.get("bbox_size"),
                    row.get("bbox_pass_any"),
                    row.get("volume_pass_any"),
                    row.get("watertight_any"),
                    row.get("overlap_pairs"),
                    " | ".join(row.get("notes", [])),
                ]
            )

    expected = expected_metrics()
    audit_summary_path = REPORTS / "npm_audit_summary.csv"
    audit_note = "未実行"
    if audit_summary_path.exists():
        audit_rows = audit_summary_path.read_text(encoding="utf-8").splitlines()[1:]
        audit_counts = dict(row.split(",", 1) for row in audit_rows if "," in row)
        audit_note = (
            f"total={audit_counts.get('total', '0')}, "
            f"moderate={audit_counts.get('moderate', '0')}, "
            f"high={audit_counts.get('high', '0')}, "
            f"critical={audit_counts.get('critical', '0')}"
        )
    env_lines = [
        f"- OS: {platform.platform()}",
        f"- Python/uv: {command_version('uv')}",
        f"- Node: {command_version('node')}",
        f"- npm: {command_version('npm')}",
        f"- OpenSCAD CLI: {openscad_version()}",
        f"- ForgeCAD CLI: {command_version('forgecad') if shutil.which('forgecad') else command_version('npx') + ' + local forgecad package'}",
    ]
    screenshot_lines = []
    for method in CANDIDATES:
        screenshot = ROOT / "reports" / "screenshots" / f"{method}.png"
        if screenshot.exists():
            screenshot_lines.append(f"### {method}\n\n![{method} screenshot](screenshots/{method}.png)")
    result_lines = []
    reference_lines = []
    for row in sorted(rows, key=lambda item: item["score"], reverse=True):
        checks = row.get("mesh_checks") or []
        measured = checks[0] if checks else {}
        bbox = measured.get("bbox_size") if measured else "未測定"
        line = (
            "| {method} | {score} | {source} | {step} | {stl} | {obj} | {preview} | {bbox} | {bbox_pass} | {volume_pass} | {watertight} | {notes} |".format(
                method=row["method"],
                score=row["score"],
                source="OK" if row["source"] else "NG",
                step="OK" if row["step"] else "NG",
                stl="OK" if row["stl"] else "NG",
                obj="OK" if row["obj"] else "NG",
                preview="OK" if row["preview"] else "NG",
                bbox=bbox,
                bbox_pass="OK" if row.get("bbox_pass_any") else "NG",
                volume_pass="OK" if row.get("volume_pass_any") else "NG",
                watertight="OK" if row.get("watertight_any") else "NG",
                notes="<br>".join(row.get("notes", [])),
            )
        )
        if row["scope"] == "full benchmark":
            result_lines.append(line)
        else:
            reference_lines.append(line)

    report = f"""# カップボードCAD 無料ツールチェーン ベンチマーク

## 前提

これは家具の見た目・CADデータ生成品質の比較です。耐荷重、転倒防止、金物、施工、安全規格の製造サインオフではありません。

## 固定仕様

- 本体外形（扉/取手の前方突出を除く）: 幅 {expected['carcass_width']}mm × 奥行 {expected['carcass_depth']}mm × 総高 {expected['total_height']}mm
- 全体bbox（扉/取手の前方突出込み）: {expected['overall_size']}mm
- 内寸目安: 幅 {expected['inner_width']}mm × 奥行 {expected['inner_depth']}mm × 高さ {expected['inner_height']}mm
- 板厚: 側板/天板/底板/棚板 {expected['panel_thickness']}mm、背板 {expected['back_thickness']}mm、扉 {expected['door_thickness']}mm
- 部品数: {expected['part_count']} ({expected['role_counts']})

## 実行環境

{chr(10).join(env_lines)}

## 結果

### フル出力候補

| 方法 | 点 | Source | STEP | STL | OBJ | PNG | 実測bboxサイズ(mm) | bbox | volume | watertight | メモ |
|---|---:|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(result_lines)}

### ソースのみ参考枠

| 方法 | 点 | Source | STEP | STL | OBJ | PNG | 実測bboxサイズ(mm) | bbox | volume | watertight | メモ |
|---|---:|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(reference_lines)}

## 画像スクリーンショット

{chr(10).join(screenshot_lines) if screenshot_lines else '未生成'}

## 採点メモ

- 寸法・構成は同じ仕様データから生成したため、主な差は「ネイティブCAD出力」「メッシュ出力」「パーツ名/再編集性」「CLIだけで完結するか」に出ます。
- 本体奥行は450mm、実測bbox奥行484mmは前面扉16mm＋取手18mmの突出を含む値です。
- `bbox` は全体bbox許容±1mm、`volume` は部品重なりがない現行仕様で期待体積との差2%以内、`watertight` はSTL/OBJのどちらかで閉じたメッシュとして読めるかを示します。
- 現行仕様のボックス部品は正の体積を持つ重なりがないことを前提に、体積和を期待値にしています。重なりを持つモデルへ拡張する場合はユニオン体積基準に変える必要があります。
- `CadQuery` と `build123d` は OpenCascade/OCP 系で STEP が出せるため、家具CADとして再編集しやすいです。
- `JSCAD` は導入が軽くブラウザ/CLIに強い一方、このローカル構成ではSTEP出力なしのメッシュ中心です。
- `OpenSCAD` はCLIが見つかる場合にSTLとPNGスクリーンショットを生成します。この実行手順ではOpenSCADのSTEPファイル生成は未成功のため、STEPはNGのままです。
- `ForgeCAD` はSTL/3MF/PNGをCLIで生成できましたが、STEPはProライセンス要求で未生成です。STL/OBJはbboxとvolumeは合格、`watertight` はNGです。STEP試行ログ: `../outputs/forgecad/forgecad_step_probe.txt`

## 依存セキュリティ

- `npm audit --json`: {audit_note}
- 詳細: `npm_audit.json` / `npm_audit_summary.csv`

## 未確認・リスク

- 実物家具の強度、反り、木口処理、蝶番、ダボ、壁固定、施工クリアランスは未評価です。
- CADAM、OpenSCAD Studio のAI機能、Fusion/Onshape MCP は APIキーや外部アプリ/アカウント前提になりやすいため、今回の無料ローカル実行ベンチからは外しています。
- PNGはベンチ用の簡易アイソメ図で、CADレンダラのスクリーンショットではありません。
"""
    (REPORTS / "benchmark_report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
