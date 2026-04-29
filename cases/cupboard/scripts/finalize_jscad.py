from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.exports import render_preview_png, write_manifest
from cupboard_benchmark.spec import cupboard_parts


OUT = ROOT / "outputs" / "jscad"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    preview_path = OUT / "cupboard_preview.png"
    render_preview_png(cupboard_parts(), preview_path, "JSCAD cupboard benchmark")
    write_manifest(
        "JSCAD",
        OUT,
        {
            "source": "designs/cupboard.jscad",
            "step": None,
            "stl": "outputs/jscad/cupboard.stl" if (OUT / "cupboard.stl").exists() else None,
            "obj": "outputs/jscad/cupboard.obj" if (OUT / "cupboard.obj").exists() else None,
            "preview": str(preview_path.relative_to(ROOT)),
        },
        ["JSCAD is mesh/CSG oriented here; STEP output is not part of this local CLI run."],
    )


if __name__ == "__main__":
    main()
