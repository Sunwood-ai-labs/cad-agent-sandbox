from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.tools import find_openscad


REPORT = ROOT / "reports" / "openscad_step_probe.csv"


def clean(value: str) -> str:
    return " ".join(value.replace("\r", " ").replace("\n", " ").split())


def main() -> None:
    openscad = find_openscad()
    source = ROOT / "designs" / "cupboard.scad"
    target = ROOT / "outputs" / "openscad" / "cupboard.step"
    if target.exists():
        target.unlink()
    if not openscad:
        REPORT.write_text("status,returncode,target_exists,stderr\nmissing_openscad,,,openscad not found\n", encoding="utf-8")
        raise SystemExit(0)
    result = subprocess.run(
        [openscad, "-o", str(target), str(source)],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    target_exists = target.exists() and target.stat().st_size > 0
    status = "generated" if result.returncode == 0 and target_exists else "not_generated"
    REPORT.write_text(
        "status,returncode,target_exists,stderr\n"
        f"{status},{result.returncode},{target_exists},{clean(result.stderr)}\n",
        encoding="utf-8",
    )
    print(REPORT)


if __name__ == "__main__":
    main()

