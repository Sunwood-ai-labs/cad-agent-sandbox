from __future__ import annotations

import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def find_openscad() -> str | None:
    env_value = os.environ.get("OPENSCAD_BIN")
    if env_value and Path(env_value).exists():
        return env_value
    path_value = shutil.which("openscad")
    if path_value:
        return path_value
    local_candidates = [
        ROOT / "tools" / "OpenSCAD-2021.01-x86-64" / "openscad-2021.01" / "openscad.exe",
        ROOT / "tools" / "OpenSCAD" / "openscad.exe",
    ]
    for candidate in local_candidates:
        if candidate.exists():
            return str(candidate)
    return None

