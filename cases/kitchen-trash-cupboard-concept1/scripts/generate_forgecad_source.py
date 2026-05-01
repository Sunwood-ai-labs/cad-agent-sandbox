from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.spec import cupboard_parts


DESIGN_PATH = ROOT / "designs" / "cupboard.forge.js"


def hex_color(color: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in color)


def main() -> None:
    DESIGN_PATH.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        {
            "name": part.name,
            "role": part.role,
            "position": [part.x + part.dx / 2, part.y + part.dy / 2, part.z],
            "size": [part.dx, part.dy, part.dz],
            "color": hex_color(part.color),
        }
        for part in cupboard_parts()
    ]
    source = f"""// Cupboard benchmark generated for ForgeCAD CLI.
// Units: millimeters. Coordinate system: X width, Y depth, Z up.

const parts = {json.dumps(parts, indent=2)};

return parts.map((part) => ({{
  name: part.name,
  role: part.role,
  shape: box(part.size[0], part.size[1], part.size[2])
    .translate(part.position[0], part.position[1], part.position[2])
    .color(part.color),
}}));
"""
    DESIGN_PATH.write_text(source, encoding="utf-8")
    print(DESIGN_PATH)


if __name__ == "__main__":
    main()
