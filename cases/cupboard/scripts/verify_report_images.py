from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from PIL import ImageStat


CASE_ROOT = Path(__file__).resolve().parents[1]
ROOT = CASE_ROOT.parents[1]
MARKDOWN_FILES = [
    CASE_ROOT / "reports" / "benchmark_report.md",
    CASE_ROOT / "README.md",
    ROOT / "README.md",
]
OUTPUT = CASE_ROOT / "reports" / "report_image_check.csv"


def main() -> None:
    rows = ["source,path,status,width,height,nonblank"]
    for markdown_file in MARKDOWN_FILES:
        text = markdown_file.read_text(encoding="utf-8")
        links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
        source = markdown_file.relative_to(ROOT)
        for link in links:
            path = (markdown_file.parent / link).resolve()
            try:
                with Image.open(path) as image:
                    extrema = ImageStat.Stat(image.convert("L")).extrema[0]
                    nonblank = extrema[0] != extrema[1]
                    rows.append(f"{source},{link},ok,{image.width},{image.height},{nonblank}")
            except Exception as exc:
                rows.append(f"{source},{link},error:{type(exc).__name__},,,False")
    OUTPUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(OUTPUT)
    if any(",error:" in row for row in rows) or any(row.endswith(",False") for row in rows[1:]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
