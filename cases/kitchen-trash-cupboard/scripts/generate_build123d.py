from __future__ import annotations

from pathlib import Path
import sys

from build123d import Box, Compound, Location, export_step, export_stl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.exports import render_preview_png, write_manifest, write_obj
from cupboard_benchmark.spec import cupboard_parts


OUT = ROOT / "outputs" / "build123d"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parts = cupboard_parts()
    solids = []
    for part in parts:
        solid = Location(part.center) * Box(part.dx, part.dy, part.dz)
        solid.label = part.name
        solids.append(solid)

    model = Compound(children=solids, label="build123d_cupboard")
    step_path = OUT / "cupboard.step"
    stl_path = OUT / "cupboard.stl"
    obj_path = OUT / "cupboard.obj"
    preview_path = OUT / "cupboard_preview.png"

    export_step(model, step_path)
    export_stl(model, stl_path, tolerance=0.2, angular_tolerance=0.2)
    write_obj(parts, obj_path)
    render_preview_png(parts, preview_path, "build123d cupboard benchmark")

    write_manifest(
        "build123d",
        OUT,
        {
            "source": "scripts/generate_build123d.py",
            "step": str(step_path.relative_to(ROOT)),
            "stl": str(stl_path.relative_to(ROOT)),
            "obj": str(obj_path.relative_to(ROOT)),
            "preview": str(preview_path.relative_to(ROOT)),
        },
        ["build123d exports STEP and STL through OpenCascade/OCP."],
    )


if __name__ == "__main__":
    main()
