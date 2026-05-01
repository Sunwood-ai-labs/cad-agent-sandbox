from __future__ import annotations

import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import trimesh
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.exports import ensure_dir, write_parts_csv
from cupboard_benchmark.spec import BoxPart, cupboard_parts, expected_metrics
from cupboard_benchmark.tools import find_openscad
from cupboard_benchmark.validation import positive_overlap_pairs


REPORTS = ROOT / "reports"
CANDIDATES = ["cadquery", "build123d", "jscad", "openscad", "forgecad"]
SCORE_WEIGHTS = {
    "concept_layout": 25,
    "visual_detail": 35,
    "cad_output": 25,
    "evidence": 15,
}


def file_ok(path: Path | None) -> bool:
    return bool(path and path.exists() and path.stat().st_size > 0)


def rel_path(raw: str | None) -> Path | None:
    if not raw:
        return None
    return ROOT / raw


def image_ok(path: Path | None) -> bool:
    if not file_ok(path):
        return False
    try:
        with Image.open(path) as image:
            extrema = image.convert("L").getextrema()
            return extrema[0] != extrema[1]
    except Exception:
        return False


def image_metrics(path: Path | None) -> dict[str, object]:
    metrics: dict[str, object] = {
        "exists": False,
        "width": 0,
        "height": 0,
        "nonblank": False,
        "nonwhite_ratio": 0.0,
        "edge_density": 0.0,
        "unique_color_sample": 0,
        "sha256_12": "",
    }
    if not file_ok(path):
        return metrics
    try:
        fingerprint = file_fingerprint(path)
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            gray = rgb.convert("L")
            metrics["exists"] = True
            metrics["width"] = image.width
            metrics["height"] = image.height
            extrema = gray.getextrema()
            metrics["nonblank"] = extrema[0] != extrema[1]

            small = gray.resize((160, 160), Image.Resampling.LANCZOS)
            pixels = list(small.tobytes())
            nonwhite = sum(1 for value in pixels if value < 245)
            metrics["nonwhite_ratio"] = round(nonwhite / len(pixels), 4)

            edge_count = 0
            comparisons = 0
            for y in range(160):
                row = y * 160
                for x in range(159):
                    if abs(pixels[row + x] - pixels[row + x + 1]) > 18:
                        edge_count += 1
                    comparisons += 1
            for y in range(159):
                row = y * 160
                next_row = (y + 1) * 160
                for x in range(160):
                    if abs(pixels[row + x] - pixels[next_row + x]) > 18:
                        edge_count += 1
                    comparisons += 1
            metrics["edge_density"] = round(edge_count / comparisons, 4)

            color_sample = rgb.resize((96, 96), Image.Resampling.LANCZOS)
            raw_colors = color_sample.tobytes()
            metrics["unique_color_sample"] = len({raw_colors[index : index + 3] for index in range(0, len(raw_colors), 3)})
            metrics["sha256_12"] = fingerprint["sha256_12"]
    except Exception:
        return metrics
    return metrics


def rendered_color_points(metrics: dict[str, object]) -> float:
    if not metrics.get("nonblank"):
        return 0
    unique = int(metrics.get("unique_color_sample", 0))
    nonwhite = float(metrics.get("nonwhite_ratio", 0))
    if unique >= 256 and nonwhite >= 0.08:
        return 3
    if unique >= 96 and nonwhite >= 0.05:
        return 2
    return 1


def rendered_complexity_points(metrics: dict[str, object]) -> float:
    if not metrics.get("nonblank"):
        return 0
    edge = float(metrics.get("edge_density", 0))
    nonwhite = float(metrics.get("nonwhite_ratio", 0))
    if edge >= 0.035 and nonwhite >= 0.08:
        return 3
    if edge >= 0.02 and nonwhite >= 0.05:
        return 2
    return 1


def file_fingerprint(path: Path | None) -> dict[str, object]:
    if not file_ok(path):
        return {"exists": False, "size": 0, "mtime_utc": "", "sha256_12": ""}
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    mtime = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    return {
        "exists": True,
        "size": path.stat().st_size,
        "mtime_utc": mtime,
        "sha256_12": digest.hexdigest()[:12],
    }


def run_timestamp() -> datetime | None:
    path = REPORTS / "run_all_last_result.csv"
    if not path.exists():
        return None
    rows = path.read_text(encoding="utf-8").splitlines()
    if len(rows) < 2:
        return None
    try:
        return datetime.fromisoformat(rows[1].split(",", 1)[0])
    except Exception:
        return None


def freshness_status(path: Path | None, run_time: datetime | None) -> str:
    if not file_ok(path):
        return "missing"
    if run_time is None:
        return "unknown"
    mtime = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    if mtime > run_time and (mtime - run_time).total_seconds() > 300:
        return "newer_than_last_full_run"
    if (run_time - mtime).total_seconds() > 24 * 60 * 60:
        return "stale_over_24h_before_last_full_run"
    return "current_window"


def parts_from_manifest(manifest: dict[str, object]) -> list[BoxPart]:
    raw_parts = manifest.get("parts")
    if not isinstance(raw_parts, list):
        return cupboard_parts()
    parts: list[BoxPart] = []
    for raw in raw_parts:
        if not isinstance(raw, dict):
            continue
        color = raw.get("color", [128, 128, 128])
        if not isinstance(color, list) or len(color) != 3:
            color = [128, 128, 128]
        try:
            parts.append(
                BoxPart(
                    name=str(raw["name"]),
                    role=str(raw["role"]),
                    x=float(raw["x"]),
                    y=float(raw["y"]),
                    z=float(raw["z"]),
                    dx=float(raw["dx"]),
                    dy=float(raw["dy"]),
                    dz=float(raw["dz"]),
                    color=(int(color[0]), int(color[1]), int(color[2])),
                )
            )
        except Exception:
            continue
    return parts or cupboard_parts()


def role_counts_from_parts(parts: list[BoxPart]) -> dict[str, int]:
    role_counts: dict[str, int] = {}
    for part in parts:
        role_counts[part.role] = role_counts.get(part.role, 0) + 1
    return role_counts


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


def score_status(points: float, max_points: float) -> str:
    if points >= max_points:
        return "pass"
    if points > 0:
        return "partial"
    return "fail"


def add_item(
    items: list[dict[str, object]],
    category: str,
    item: str,
    points: float,
    max_points: float,
    evidence: str,
) -> None:
    if points < 0 or points > max_points:
        raise ValueError(f"Invalid score for {category}:{item}: {points}/{max_points}")
    items.append(
        {
            "category": category,
            "item": item,
            "points": points,
            "max_points": max_points,
            "status": score_status(points, max_points),
            "evidence": evidence,
        }
    )


def category_total(items: list[dict[str, object]], category: str) -> float:
    return round(sum(float(item["points"]) for item in items if item["category"] == category), 2)


def grade_for(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def top_penalties(items: list[dict[str, object]], limit: int = 4) -> list[str]:
    penalties = []
    for item in items:
        missing = float(item["max_points"]) - float(item["points"])
        if missing > 0:
            penalties.append((missing, f"{item['category']}:{item['item']} -{missing:g}"))
    penalties.sort(reverse=True)
    return [entry for _, entry in penalties[:limit]]


def score_candidate(manifest: dict[str, object], output_dir: Path) -> dict[str, object]:
    files = manifest.get("generated_files", {})
    source = rel_path(files.get("source")) if isinstance(files, dict) else None
    step = rel_path(files.get("step")) if isinstance(files, dict) else None
    stl = rel_path(files.get("stl")) if isinstance(files, dict) else None
    obj = rel_path(files.get("obj")) if isinstance(files, dict) else None
    preview = rel_path(files.get("preview")) if isinstance(files, dict) else None
    expected_spec = expected_metrics()
    spec = manifest.get("spec") if isinstance(manifest.get("spec"), dict) else expected_spec
    parts = parts_from_manifest(manifest)
    part_by_name = {part.name: part for part in parts}
    role_counts = role_counts_from_parts(parts)
    expected_overall_size = expected_spec["overall_size"]
    actual_metrics = {
        "upper_front_y": part_by_name.get("upper_left_side").y if part_by_name.get("upper_left_side") else None,
        "upper_door_y": part_by_name.get("upper_left_door").y if part_by_name.get("upper_left_door") else None,
        "upper_back_y": part_by_name.get("upper_back_panel").y if part_by_name.get("upper_back_panel") else None,
        "upper_storage_inner_depth": part_by_name.get("upper_center_divider").dy if part_by_name.get("upper_center_divider") else None,
        "counter_top_height": (part_by_name.get("trash_counter_deck").z + part_by_name.get("trash_counter_deck").dz) if part_by_name.get("trash_counter_deck") else None,
        "counter_depth": part_by_name.get("trash_counter_deck").dy if part_by_name.get("trash_counter_deck") else None,
        "pegboard_y": part_by_name.get("middle_pegboard").y if part_by_name.get("middle_pegboard") else None,
        "trash_bay_clear_depth": part_by_name.get("trash_bay_divider_1").dy if part_by_name.get("trash_bay_divider_1") else None,
        "trash_bay_clear_height": part_by_name.get("trash_bay_divider_1").dz if part_by_name.get("trash_bay_divider_1") else None,
    }
    overlap_pairs = positive_overlap_pairs(parts)
    expected_volume = sum(part.dx * part.dy * part.dz for part in parts)

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

    items: list[dict[str, object]] = []
    measured_bbox = (mesh_checks[0].get("bbox_size") if mesh_checks else None)
    method_key = str(manifest.get("method", "")).lower()
    comparison_path = REPORTS / f"concept_vs_{method_key}.png"
    screenshot_path = REPORTS / "screenshots" / f"{method_key}.png"
    screenshot_metrics = image_metrics(screenshot_path)
    add_item(
        items,
        "concept_layout",
        "overall W1680 D650 H1800 envelope",
        6 if bbox_pass_any else (2 if file_ok(source) else 0),
        6,
        f"measured bbox={measured_bbox}, expected={expected_overall_size}, tolerance=1mm",
    )
    upper_setback_ok = (
        actual_metrics["upper_front_y"] is not None
        and actual_metrics["upper_door_y"] is not None
        and actual_metrics["upper_back_y"] is not None
        and actual_metrics["upper_storage_inner_depth"] is not None
        and abs(float(actual_metrics["upper_front_y"]) - 360.0) <= 0.1
        and abs(float(actual_metrics["upper_door_y"]) - 344.0) <= 0.1
        and abs(float(actual_metrics["upper_back_y"]) - 644.0) <= 0.1
        and abs(float(actual_metrics["upper_storage_inner_depth"]) - 284.0) <= 0.1
    )
    add_item(
        items,
        "concept_layout",
        "D290 upper storage set back from front",
        5 if file_ok(source) and upper_setback_ok else 0,
        5,
        f"upper_front_y={actual_metrics['upper_front_y']}, upper_door_y={actual_metrics['upper_door_y']}, upper_back_y={actual_metrics['upper_back_y']}",
    )
    counter_ok = (
        actual_metrics["counter_top_height"] is not None
        and actual_metrics["counter_depth"] is not None
        and abs(float(actual_metrics["counter_top_height"]) - 900.0) <= 0.1
        and abs(float(actual_metrics["counter_depth"]) - 450.0) <= 0.1
    )
    add_item(
        items,
        "concept_layout",
        "counter H900 and D450 work deck",
        4 if file_ok(source) and counter_ok else 0,
        4,
        f"counter_top_height={actual_metrics['counter_top_height']}, counter_depth={actual_metrics['counter_depth']}",
    )
    trash_space_ok = (
        expected_spec["trash_bay_columns"] == 3
        and abs(float(expected_spec["trash_bay_clear_width_each"]) - 520.0) <= 0.1
        and actual_metrics["trash_bay_clear_depth"] is not None
        and actual_metrics["trash_bay_clear_height"] is not None
        and abs(float(actual_metrics["trash_bay_clear_depth"]) - 600.0) <= 0.1
        and abs(float(actual_metrics["trash_bay_clear_height"]) - 740.0) <= 0.1
    )
    add_item(
        items,
        "concept_layout",
        "three open trash bays with 45L-class clearance",
        5 if file_ok(source) and trash_space_ok else 0,
        5,
        f"columns={expected_spec['trash_bay_columns']}, clear_each={expected_spec['trash_bay_clear_width_each']}x{actual_metrics['trash_bay_clear_depth']}x{actual_metrics['trash_bay_clear_height']}",
    )
    peg_layout_ok = actual_metrics["pegboard_y"] is not None and abs(float(actual_metrics["pegboard_y"]) - 644.0) <= 0.1 and role_counts.get("peg_hole", 0) >= 50
    add_item(
        items,
        "concept_layout",
        "rear pegboard position above counter",
        3 if file_ok(source) and peg_layout_ok else 0,
        3,
        f"pegboard_y={actual_metrics['pegboard_y']}, peg_holes={role_counts.get('peg_hole', 0)}",
    )
    add_item(
        items,
        "concept_layout",
        "no positive-volume part overlaps",
        2 if file_ok(source) and not overlap_pairs else 0,
        2,
        f"positive_overlap_pairs={len(overlap_pairs)}",
    )

    source_available = file_ok(source)
    add_item(
        items,
        "visual_detail",
        "upper two-door face and internal shelves",
        3 if source_available and role_counts.get("door") == 2 and role_counts.get("shelf", 0) >= 4 else 0,
        4,
        "two slab doors and shelves exist, but hinges and pull hardware are simplified",
    )
    add_item(
        items,
        "visual_detail",
        "pegboard, outlet, slide cover, and towel zone",
        4 if source_available and role_counts.get("peg_hole", 0) >= 50 and role_counts.get("outlet", 0) >= 4 else 0,
        6,
        f"peg_holes={role_counts.get('peg_hole', 0)}, outlet_parts={role_counts.get('outlet', 0)}, towel_parts={role_counts.get('towel', 0)}",
    )
    add_item(
        items,
        "visual_detail",
        "counter appliances and small morning objects",
        3 if source_available and role_counts.get("counter_appliance", 0) >= 8 and role_counts.get("counter_decor", 0) >= 6 else 0,
        7,
        "toaster/kettle/mug/glass/plant placeholders exist, but curved bodies are box approximations",
    )
    add_item(
        items,
        "visual_detail",
        "three colored bins, lids, and front labels",
        4 if source_available and role_counts.get("trash_bin") == 3 and role_counts.get("bin_label", 0) >= 9 else 0,
        6,
        "green/blue/gray bins and symbolic labels exist, but printed Japanese label graphics are not reproduced",
    )
    add_item(
        items,
        "visual_detail",
        "materials and color palette",
        rendered_color_points(screenshot_metrics),
        5,
        "rendered screenshot metrics: unique_color_sample={unique}, nonwhite_ratio={nonwhite}; flat colors are present but wood grain/fabric texture are not modeled".format(
            unique=screenshot_metrics.get("unique_color_sample"),
            nonwhite=screenshot_metrics.get("nonwhite_ratio"),
        ),
    )
    add_item(
        items,
        "visual_detail",
        "fine hardware, labels, curves, and fabric realism",
        0,
        5,
        "box-primitive CAD does not reproduce rounded appliances, cloth folds, exact icons, or detailed metal fittings",
    )
    add_item(
        items,
        "visual_detail",
        "overall catalog silhouette readability",
        min(2, rendered_complexity_points(screenshot_metrics)),
        2,
        "rendered screenshot metrics: edge_density={edge}, nonwhite_ratio={nonwhite}; silhouette is readable but still simplified".format(
            edge=screenshot_metrics.get("edge_density"),
            nonwhite=screenshot_metrics.get("nonwhite_ratio"),
        ),
    )

    add_item(
        items,
        "cad_output",
        "source file and manifest reproducibility",
        (3 if file_ok(source) else 0) + (2 if file_ok(output_dir / "manifest.json") else 0),
        5,
        f"source={file_ok(source)}, manifest={file_ok(output_dir / 'manifest.json')}",
    )
    mesh_export_points = 0
    mesh_export_points += 3 if file_ok(stl) else 0
    mesh_export_points += 2 if file_ok(obj) else 0
    add_item(items, "cad_output", "mesh exports", mesh_export_points, 5, f"stl={file_ok(stl)}, obj={file_ok(obj)}")
    add_item(items, "cad_output", "STEP/native exchange output", 5 if file_ok(step) else 0, 5, f"step={file_ok(step)}")
    add_item(
        items,
        "cad_output",
        "measured mesh bbox and volume checks",
        5 if bbox_pass_any and volume_pass_any else (3 if bbox_pass_any else 0),
        5,
        f"bbox_pass={bbox_pass_any}, volume_pass={volume_pass_any}",
    )
    add_item(items, "cad_output", "watertight mesh", 3 if watertight_any else 0, 3, f"watertight_any={watertight_any}")
    add_item(
        items,
        "cad_output",
        "measurement completed without parser error",
        2 if mesh_checks and not measurement_error else 0,
        2,
        f"mesh_checks={len(mesh_checks)}, measurement_error={measurement_error}",
    )

    concept_path = ROOT / "concepts" / "exports" / "concept_sheet_01_family_unit.png"
    add_item(items, "evidence", "attached concept image is present and nonblank", 3 if image_ok(concept_path) else 0, 3, str(concept_path.relative_to(ROOT)))
    add_item(items, "evidence", "side-by-side concept/CAD comparison image", 3 if image_ok(comparison_path) else 0, 3, str(comparison_path.relative_to(ROOT)))
    add_item(items, "evidence", "candidate screenshot is present and nonblank", 3 if image_ok(screenshot_path) else 0, 3, str(screenshot_path.relative_to(ROOT)))
    item_rows_ready = len(items) >= 18 and all(item.get("evidence") for item in items)
    add_item(
        items,
        "evidence",
        "itemized scoring evidence exists before summary export",
        3 if item_rows_ready else 0,
        3,
        f"{len(items)} method-specific items prepared before score_items.csv export",
    )
    visual_penalty_count = sum(1 for item in items if item["category"] == "visual_detail" and item["status"] != "pass")
    add_item(
        items,
        "evidence",
        "limitations are represented as scored visual penalties",
        3 if visual_penalty_count else 0,
        3,
        f"{visual_penalty_count} visual_detail penalties/partials recorded; non-scored limits are separated in reports/non_scored_limits.csv",
    )

    category_scores = {category: category_total(items, category) for category in SCORE_WEIGHTS}
    score = round(sum(category_scores.values()), 2)
    notes = list(manifest.get("notes", []))
    notes.append(
        "Score uses itemized weighted criteria; visual/detail penalties reflect box-primitive CAD limits instead of an arbitrary score cap."
    )
    run_time = run_timestamp()
    output_files = []
    for label, path in {
        "source": source,
        "step": step,
        "stl": stl,
        "obj": obj,
        "preview": preview,
        "screenshot": screenshot_path,
        "concept_comparison": comparison_path,
    }.items():
        fingerprint = file_fingerprint(path)
        freshness = freshness_status(path, run_time)
        if label == "source" and fingerprint["exists"]:
            freshness = "source_reference"
        output_files.append(
            {
                "method": manifest.get("method"),
                "label": label,
                "path": str(path.relative_to(ROOT)) if path and path.exists() else "",
                "freshness": freshness,
                **fingerprint,
            }
        )

    return {
        "method": manifest.get("method"),
        "scope": "source-only reference" if not mesh_checks else "full benchmark",
        "score": score,
        "grade": grade_for(score),
        "category_scores": category_scores,
        "score_items": items,
        "output_files": output_files,
        "top_penalties": top_penalties(items),
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
        "notes": notes,
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


def build_visual_comparison(method: str, screenshot_path: Path, output_path: Path) -> Path | None:
    concept_path = ROOT / "concepts" / "exports" / "concept_sheet_01_family_unit.png"
    if not concept_path.exists() or not screenshot_path.exists():
        return None

    def fit(image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
        image = image.convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image

    concept = fit(Image.open(concept_path), (1040, 760))
    screenshot = fit(Image.open(screenshot_path), (1040, 760))
    label_h = 56
    gutter = 36
    margin = 32
    width = margin * 2 + concept.width + gutter + screenshot.width
    height = margin * 2 + label_h + max(concept.height, screenshot.height)
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin), "Attached concept sheet", fill=(40, 40, 40))
    screenshot_x = margin + concept.width + gutter
    draw.text((screenshot_x, margin), f"Regenerated {method} output after feedback", fill=(40, 40, 40))
    canvas.paste(concept, (margin, margin + label_h))
    canvas.paste(screenshot, (screenshot_x, margin + label_h))
    draw.rectangle((margin, margin + label_h, margin + concept.width - 1, margin + label_h + concept.height - 1), outline=(120, 120, 120), width=2)
    draw.rectangle((screenshot_x, margin + label_h, screenshot_x + screenshot.width - 1, margin + label_h + screenshot.height - 1), outline=(120, 120, 120), width=2)
    canvas.save(output_path)
    return output_path


def build_visual_comparisons() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for method in CANDIDATES:
        method_key = method.lower()
        screenshot_path = REPORTS / "screenshots" / f"{method_key}.png"
        output_path = REPORTS / f"concept_vs_{method_key}.png"
        comparison = build_visual_comparison(method, screenshot_path, output_path)
        if comparison:
            paths[method_key] = comparison
    return paths


def main() -> None:
    ensure_dir(REPORTS)
    comparison_paths = build_visual_comparisons()
    write_parts_csv(REPORTS / "parts_inventory.csv")
    rows = []
    for candidate in CANDIDATES:
        output_dir = ROOT / "outputs" / candidate
        manifest_path = output_dir / "manifest.json"
        if not manifest_path.exists():
            rows.append(
                {
                    "method": candidate,
                    "scope": "missing",
                    "score": 0,
                    "grade": "F",
                    "category_scores": {category: 0 for category in SCORE_WEIGHTS},
                    "score_items": [],
                    "output_files": [],
                    "top_penalties": ["manifest missing"],
                    "source": False,
                    "step": False,
                    "stl": False,
                    "obj": False,
                    "preview": False,
                    "mesh_checks": [],
                    "bbox_pass_any": False,
                    "volume_pass_any": False,
                    "watertight_any": False,
                    "overlap_pairs": [],
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
        writer.writerow(
            [
                "method",
                "scope",
                "score",
                "grade",
                "concept_layout",
                "visual_detail",
                "cad_output",
                "evidence",
                "source",
                "step",
                "stl",
                "obj",
                "preview",
                "bbox_min",
                "bbox_max",
                "bbox_size",
                "bbox_pass",
                "volume_pass",
                "watertight_any",
                "overlap_pairs",
                "top_penalties",
                "notes",
            ]
        )
        for row in rows:
            measured = (row.get("mesh_checks") or [{}])[0]
            categories = row.get("category_scores", {})
            writer.writerow(
                [
                    row["method"],
                    row["scope"],
                    row["score"],
                    row.get("grade"),
                    categories.get("concept_layout", 0),
                    categories.get("visual_detail", 0),
                    categories.get("cad_output", 0),
                    categories.get("evidence", 0),
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
                    " | ".join(row.get("top_penalties", [])),
                    " | ".join(row.get("notes", [])),
                ]
            )

    breakdown_path = REPORTS / "score_breakdown.csv"
    with breakdown_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "method",
                "total_score",
                "grade",
                "concept_layout",
                "concept_layout_max",
                "visual_detail",
                "visual_detail_max",
                "cad_output",
                "cad_output_max",
                "evidence",
                "evidence_max",
                "top_penalties",
            ]
        )
        for row in rows:
            categories = row.get("category_scores", {})
            writer.writerow(
                [
                    row["method"],
                    row["score"],
                    row.get("grade"),
                    categories.get("concept_layout", 0),
                    SCORE_WEIGHTS["concept_layout"],
                    categories.get("visual_detail", 0),
                    SCORE_WEIGHTS["visual_detail"],
                    categories.get("cad_output", 0),
                    SCORE_WEIGHTS["cad_output"],
                    categories.get("evidence", 0),
                    SCORE_WEIGHTS["evidence"],
                    " | ".join(row.get("top_penalties", [])),
                ]
            )

    items_path = REPORTS / "score_items.csv"
    with items_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["method", "category", "item", "points", "max_points", "status", "evidence"])
        for row in rows:
            for item in row.get("score_items", []):
                writer.writerow(
                    [
                        row["method"],
                        item["category"],
                        item["item"],
                        item["points"],
                        item["max_points"],
                        item["status"],
                        item["evidence"],
                    ]
                )

    file_inventory_path = REPORTS / "output_file_fingerprints.csv"
    with file_inventory_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["method", "label", "path", "exists", "size", "mtime_utc", "sha256_12", "freshness"])
        for row in rows:
            for file_row in row.get("output_files", []):
                writer.writerow(
                    [
                        file_row.get("method"),
                        file_row.get("label"),
                        file_row.get("path"),
                        file_row.get("exists"),
                        file_row.get("size"),
                        file_row.get("mtime_utc"),
                        file_row.get("sha256_12"),
                        file_row.get("freshness"),
                    ]
                )

    image_metrics_path = REPORTS / "image_metrics.csv"
    image_metric_targets = [("concept", "concept", ROOT / "concepts" / "exports" / "concept_sheet_01_family_unit.png")]
    for method in CANDIDATES:
        image_metric_targets.append((method, "screenshot", REPORTS / "screenshots" / f"{method}.png"))
        image_metric_targets.append((method, "concept_comparison", REPORTS / f"concept_vs_{method}.png"))
    with image_metrics_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["method", "label", "path", "exists", "width", "height", "nonblank", "nonwhite_ratio", "edge_density", "unique_color_sample", "sha256_12"])
        for method, label, path in image_metric_targets:
            metrics = image_metrics(path)
            writer.writerow(
                [
                    method,
                    label,
                    str(path.relative_to(ROOT)) if path.exists() else "",
                    metrics["exists"],
                    metrics["width"],
                    metrics["height"],
                    metrics["nonblank"],
                    metrics["nonwhite_ratio"],
                    metrics["edge_density"],
                    metrics["unique_color_sample"],
                    metrics["sha256_12"],
                ]
            )

    non_scored_limits_path = REPORTS / "non_scored_limits.csv"
    with non_scored_limits_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["item", "reason", "impact_on_score", "status"])
        writer.writerow(["Structural strength and anti-tip safety", "No material, fastener, wall-fix, or load simulation model is present.", "Excluded from score; report states this is not manufacturing sign-off.", "not_scored"])
        writer.writerow(["Real product fit and door/hardware procurement", "No vendor bins, hinges, outlets, or metal hardware catalogs are bound to the CAD.", "Excluded from score; CAD/output category only checks generated files and mesh quality.", "not_scored"])
        writer.writerow(["Photoreal texture and semantic image similarity", "No texture map, trained visual model, or annotated concept mask is available for reliable semantic similarity scoring.", "Visual/detail category uses explicit penalties and image metrics instead of claiming photoreal matching.", "partially_scored"])
        writer.writerow(["Human workflow ergonomics", "No user reach, clearance, or time-motion simulation is implemented.", "Excluded from score; concept layout checks only static geometry.", "not_scored"])

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
    comparison_image_lines = []
    for method in CANDIDATES:
        comparison = comparison_paths.get(method.lower())
        if comparison and comparison.exists():
            comparison_image_lines.append(f"### {method}\n\n![{method} concept comparison]({comparison.relative_to(REPORTS).as_posix()})")
    result_lines = []
    reference_lines = []
    for row in sorted(rows, key=lambda item: item["score"], reverse=True):
        checks = row.get("mesh_checks") or []
        measured = checks[0] if checks else {}
        bbox = measured.get("bbox_size") if measured else "未測定"
        categories = row.get("category_scores", {})
        line = (
            "| {method} | {score} | {grade} | {layout}/25 | {visual}/35 | {cad}/25 | {evidence}/15 | {source} | {step} | {stl} | {obj} | {preview} | {bbox} | {bbox_pass} | {volume_pass} | {watertight} | {penalties} |".format(
                method=row["method"],
                score=row["score"],
                grade=row.get("grade"),
                layout=categories.get("concept_layout", 0),
                visual=categories.get("visual_detail", 0),
                cad=categories.get("cad_output", 0),
                evidence=categories.get("evidence", 0),
                source="OK" if row["source"] else "NG",
                step="OK" if row["step"] else "NG",
                stl="OK" if row["stl"] else "NG",
                obj="OK" if row["obj"] else "NG",
                preview="OK" if row["preview"] else "NG",
                bbox=bbox,
                bbox_pass="OK" if row.get("bbox_pass_any") else "NG",
                volume_pass="OK" if row.get("volume_pass_any") else "NG",
                watertight="OK" if row.get("watertight_any") else "NG",
                penalties="<br>".join(row.get("top_penalties", [])),
            )
        )
        if row["scope"] == "full benchmark":
            result_lines.append(line)
        else:
            reference_lines.append(line)
    reference_section = ""
    if reference_lines:
        reference_section = f"""
### ソースのみ参考枠

| 方法 | 総合 | 等級 | レイアウト | 視覚/詳細 | CAD出力 | 証拠 | Source | STEP | STL | OBJ | PNG | 実測bboxサイズ(mm) | bbox | volume | watertight | 主な減点 |
|---|---:|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(reference_lines)}
"""

    report = f"""# ゴミ箱3台対応キッチンカップボードCAD 無料ツールチェーン ベンチマーク

## 前提

これは家具の見た目・CADデータ生成品質の比較です。耐荷重、転倒防止、ゴミ箱の実製品適合、金物、施工、安全規格の製造サインオフではありません。

## 固定仕様

- 本体外形（扉/取手の前方突出を除く）: 幅 {expected['carcass_width']}mm × 奥行 {expected['carcass_depth']}mm × 総高 {expected['total_height']}mm
- 全体bbox（扉/取手の前方突出込み）: {expected['overall_size']}mm
- 内寸目安: 幅 {expected['inner_width']}mm × 奥行 {expected['inner_depth']}mm × 高さ {expected['inner_height']}mm
- 下部ゴミ箱ベイ: {expected['trash_bay_columns']}列、1列あたり有効幅 約 {expected['trash_bay_clear_width_each']:.1f}mm × 有効奥行 {expected['trash_bay_clear_depth']}mm × 有効高さ {expected['trash_bay_clear_height']}mm
- ゴミ箱プレースホルダー: {expected['trash_bin_size']}mm × 3台
- 板厚: 側板/天板/底板/棚板 {expected['panel_thickness']}mm、背板 {expected['back_thickness']}mm、扉 {expected['door_thickness']}mm
- 部品数: {expected['part_count']} ({expected['role_counts']})

## 実行環境

{chr(10).join(env_lines)}

## 採点方式

総合点は単一の上限キャップではなく、下の4カテゴリの項目別加点で算出します。各項目の点数、満点、判定、根拠は [score_items.csv](score_items.csv) に、候補別の内訳は [score_breakdown.csv](score_breakdown.csv) に保存しています。出力ファイルのサイズ、mtime、sha256短縮値、鮮度フラグは [output_file_fingerprints.csv](output_file_fingerprints.csv) に保存しています。画像の非空率、エッジ密度、色数サンプルは [image_metrics.csv](image_metrics.csv)、採点外の重要限界は [non_scored_limits.csv](non_scored_limits.csv) に分離しています。

| カテゴリ | 配点 | 評価内容 |
|---|---:|---|
| レイアウト/寸法 | {SCORE_WEIGHTS['concept_layout']} | `W1680 x D650 x H1800`、上段 `D290` 奥寄せ、カウンター `H900/D450`、3分別ダスト空間、背面ペグボード位置、部品干渉 |
| 視覚/詳細 | {SCORE_WEIGHTS['visual_detail']} | 上段扉、棚、ペグ穴、コンセント、家電/小物、3色ゴミ箱、素材色、ラベル、曲面/布/木目の再現度。スクリーンショットの画像メトリクスも補助根拠にする |
| CAD出力 | {SCORE_WEIGHTS['cad_output']} | source/manifest、STL/OBJ、STEP、bbox/volume、watertight、測定エラーの有無 |
| 証拠/検証 | {SCORE_WEIGHTS['evidence']} | 添付コンセプト画像、手法別比較画像、候補スクリーンショット、採点CSV、限界の明示 |

等級の目安: `A >= 90`, `B >= 80`, `C >= 70`, `D >= 60`, `F < 60`。今回の共有モデルはボックス部品ベースなので、木目、丸い家電、布のしわ、正確な印字ラベル、細かい金物は視覚/詳細カテゴリで明示的に減点します。画像メトリクスは「存在確認だけ」ではなく、レンダーの密度や色分離を補助的に見るためのもので、写真意味理解の自動一致判定ではありません。

`output_file_fingerprints.csv` の `newer_than_last_full_run` は、CAD本体ではなく採点後に作る比較画像などが直近の `run_all` marker より新しい場合に出ます。これは時刻関係をそのまま記録するフラグで、CAD出力の成功判定とは分けています。

## 結果

### フル出力候補

| 方法 | 総合 | 等級 | レイアウト | 視覚/詳細 | CAD出力 | 証拠 | Source | STEP | STL | OBJ | PNG | 実測bboxサイズ(mm) | bbox | volume | watertight | 主な減点 |
|---|---:|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(result_lines)}
{reference_section}

## 添付コンセプト画像

![添付コンセプト画像: 朝活ファミリーの連携ユニット](../concepts/exports/concept_sheet_01_family_unit.png)

## 手法別コンセプト比較画像

{chr(10).join(comparison_image_lines) if comparison_image_lines else '比較画像は未生成です。'}

## コンセプト照合

- 点数はCAD生成成功だけではなく、添付コンセプトへの近さを `レイアウト/寸法` と `視覚/詳細` に分けて採点しています。共有ボックス部品モデルでは、木目テクスチャ、丸みのある家電、布のしわ、印字ラベル、金物詳細を表現しきれないため、視覚/詳細カテゴリで減点します。
- 上段収納はコンセプト側面図の `D290` に合わせ、奥側へ浅く配置しています。現行仕様では上段前面Y={expected['upper_front_y']}mm、上段扉Y={expected['upper_door_y']}mm、背板Y={expected['upper_back_y']}mmです。
- ペグボードはカウンター上から上段収納下までの背面に配置し、穴列、2口コンセント、朝家電、小物、タオル、3色ゴミ箱を再現対象にしています。
- それでも現行成果物は「5ツールで同じ構成を生成するためのCAD近似」であり、添付画像のカタログ品質そのものではありません。

## PDCA再照合

| 観点 | コンセプト画像の要件 | 修正後CADの証拠 | 判定 |
|---|---|---|---|
| 上段収納の奥行 | 側面図は上段収納を `D290` の浅い奥側収納として示している | `upper_front_y={expected['upper_front_y']}mm`, `upper_door_y={expected['upper_door_y']}mm`, `upper_back_y={expected['upper_back_y']}mm` | OK |
| 背面/ペグボード | カウンター上の背面に穴あきボード、2口コンセント、フック類がある | `pegboard_y={expected['pegboard_y']}mm`, ペグ穴{expected['role_counts'].get('peg_hole', 0)}個相当、コンセント部品あり | OK |
| 下部ダストスペース | 3分別のオープンなダストボックス空間 | 3列、緑/青/灰のゴミ箱、前面ラベル、上フタ表現あり | OK |
| 外形寸法 | `W1680 x D650 x H1800` | 5出力すべてbboxが許容内、CadQuery/build123dは `1680 x 650 x 1800` | OK |
| 点数 | カタログ画像の完全再現ではない | 単一キャップを廃止し、4カテゴリ・項目別根拠で採点。詳細は `score_items.csv` | OK |
| 残る限界 | 木目、布、家電の丸み、文字ラベル、金物質感が写真調 | 共有ボックス部品CADのため未再現。点数とメモに明記 | 残リスク |

## 画像スクリーンショット

{chr(10).join(screenshot_lines) if screenshot_lines else '未生成'}

## 採点メモ

- 寸法・構成は同じ仕様データから生成したため、主な差は「ネイティブCAD出力」「メッシュ出力」「パーツ名/再編集性」「CLIだけで完結するか」に出ます。
- 本体奥行は{expected['carcass_depth']}mm、実測bbox奥行{expected['overall_size'][1]}mmは上部扉と取手の前方突出を含む値です。
- 下部は扉を付けず、3つのゴミ箱を引き出しやすいオープンベイとして扱っています。
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
- PNGはベンチ用の簡易アイソメ図またはCLIレンダー画像で、実物色・仕上げの決定図ではありません。
"""
    (REPORTS / "benchmark_report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
