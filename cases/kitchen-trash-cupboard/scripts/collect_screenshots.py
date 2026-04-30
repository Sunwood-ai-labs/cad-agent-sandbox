from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.exports import ensure_dir


METHODS = ["cadquery", "build123d", "jscad", "openscad", "forgecad"]
REPORT_DIR = ROOT / "reports" / "screenshots"


def main() -> None:
    ensure_dir(REPORT_DIR)
    rows = ["method,path,status,source"]
    for method in METHODS:
        manifest_path = ROOT / "outputs" / method / "manifest.json"
        if not manifest_path.exists():
            rows.append(f"{method},,missing_manifest,")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = manifest.get("generated_files", {})
        source_rel = files.get("screenshot") or files.get("preview")
        if not source_rel:
            rows.append(f"{method},,missing_image,")
            continue
        source = ROOT / source_rel
        target = REPORT_DIR / f"{method}.png"
        if source.exists():
            shutil.copyfile(source, target)
            rows.append(f"{method},{target.relative_to(ROOT)},ok,{source_rel}")
        else:
            rows.append(f"{method},,missing_source,{source_rel}")
    (ROOT / "reports" / "screenshot_inventory.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(ROOT / "reports" / "screenshot_inventory.csv")


if __name__ == "__main__":
    main()
