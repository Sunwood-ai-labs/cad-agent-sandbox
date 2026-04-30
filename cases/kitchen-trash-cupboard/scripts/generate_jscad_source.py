from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.spec import cupboard_parts


DESIGN_PATH = ROOT / "designs" / "cupboard.jscad"


def main() -> None:
    DESIGN_PATH.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        {
            "name": part.name,
            "role": part.role,
            "pos": [part.x, part.y, part.z],
            "size": [part.dx, part.dy, part.dz],
        }
        for part in cupboard_parts()
    ]
    source = f"""const {{ cuboid }} = require('@jscad/modeling').primitives
const {{ translate }} = require('@jscad/modeling').transforms
const {{ union }} = require('@jscad/modeling').booleans

const parts = {json.dumps(parts, indent=2)}

const boxPart = (part) => {{
  const center = [
    part.pos[0] + part.size[0] / 2,
    part.pos[1] + part.size[1] / 2,
    part.pos[2] + part.size[2] / 2
  ]
  return translate(center, cuboid({{ size: part.size }}))
}}

const main = () => union(parts.map(boxPart))

module.exports = {{ main, parts }}
"""
    DESIGN_PATH.write_text(source, encoding="utf-8")
    print(DESIGN_PATH)


if __name__ == "__main__":
    main()
