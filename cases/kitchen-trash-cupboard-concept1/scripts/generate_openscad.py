from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.exports import render_preview_png, write_manifest
from cupboard_benchmark.spec import cupboard_parts
from cupboard_benchmark.tools import find_openscad


DESIGN_DIR = ROOT / "designs"
OUT = ROOT / "outputs" / "openscad"


def scad_color(color: tuple[int, int, int]) -> str:
    return "[" + ", ".join(f"{channel / 255:.4f}" for channel in color) + "]"


def main() -> None:
    DESIGN_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    parts = cupboard_parts()
    source_path = DESIGN_DIR / "cupboard.scad"
    preview_path = OUT / "cupboard_preview.png"
    screenshot_path = OUT / "cupboard_screenshot.png"
    stl_path = OUT / "cupboard.stl"
    obj_path = OUT / "cupboard.obj"

    lines = [
        "// Cupboard benchmark generated for OpenSCAD.",
        "// Units: millimeters. Coordinate system: X width, Y depth, Z up.",
        "$fn = 32;",
        "",
        "module part_box(label, pos, size, rgb) {",
        "  // OpenSCAD does not preserve part names in mesh output; label is kept for source readability.",
        "  color(rgb) translate(pos) cube(size, center = false);",
        "}",
        "",
    ]
    for part in parts:
        pos = f"[{part.x:.4f}, {part.y:.4f}, {part.z:.4f}]"
        size = f"[{part.dx:.4f}, {part.dy:.4f}, {part.dz:.4f}]"
        lines.append(f'part_box("{part.name}", {pos}, {size}, {scad_color(part.color)});')
    source_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    render_preview_png(parts, preview_path, "OpenSCAD cupboard benchmark")

    generated_files: dict[str, str | None] = {
        "source": str(source_path.relative_to(ROOT)),
        "step": None,
        "stl": None,
        "obj": None,
        "preview": str(preview_path.relative_to(ROOT)),
        "screenshot": None,
    }
    notes = ["OpenSCAD source was generated locally."]
    openscad = find_openscad()
    if openscad:
        subprocess.run([openscad, "-o", str(stl_path), str(source_path)], check=True)
        subprocess.run(
            [
                openscad,
                "-o",
                str(screenshot_path),
                "--imgsize=1400,1200",
                "--autocenter",
                "--viewall",
                "--projection=o",
                "--colorscheme=Cornfield",
                str(source_path),
            ],
            check=True,
        )
        try:
            import trimesh

            mesh = trimesh.load(stl_path, force="mesh")
            mesh.export(obj_path)
            generated_files["obj"] = str(obj_path.relative_to(ROOT))
            notes.append("OBJ was converted from the OpenSCAD STL using trimesh.")
        except Exception as exc:
            notes.append(f"OBJ conversion from OpenSCAD STL failed: {exc}")
        generated_files["stl"] = str(stl_path.relative_to(ROOT))
        generated_files["screenshot"] = str(screenshot_path.relative_to(ROOT))
        notes.append("OpenSCAD CLI was found; STL and PNG screenshot export completed.")
    else:
        notes.append("OpenSCAD CLI was not found on PATH; STL/STEP/OBJ export is unverified.")

    write_manifest("OpenSCAD", OUT, generated_files, notes)


if __name__ == "__main__":
    main()
