from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cadquery as cq

from cupboard_benchmark.exports import ensure_dir


REPORTS = ROOT / "reports"
STEP_FILES = {
    "CadQuery": ROOT / "outputs" / "cadquery" / "cupboard.step",
    "build123d": ROOT / "outputs" / "build123d" / "cupboard.step",
}


def main() -> None:
    ensure_dir(REPORTS)
    rows = []
    for method, path in STEP_FILES.items():
        if not path.exists():
            rows.append([method, str(path.relative_to(ROOT)), "missing", "", "", ""])
            continue
        model = cq.importers.importStep(str(path))
        bbox = model.val().BoundingBox()
        rows.append(
            [
                method,
                str(path.relative_to(ROOT)),
                "ok",
                len(model.solids().vals()),
                f"{bbox.xlen:.3f}",
                f"{bbox.ylen:.3f}",
                f"{bbox.zlen:.3f}",
            ]
        )
    with (REPORTS / "step_imports.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["method", "path", "status", "solid_count", "bbox_x", "bbox_y", "bbox_z"])
        writer.writerows(rows)
    for row in rows:
        print(",".join(map(str, row)))


if __name__ == "__main__":
    main()
