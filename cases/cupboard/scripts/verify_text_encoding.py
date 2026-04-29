from __future__ import annotations

import csv
from pathlib import Path


CASE_ROOT = Path(__file__).resolve().parents[1]
ROOT = CASE_ROOT.parents[1]
EXCLUDED_DIRS = {".venv", "node_modules", "tools"}
MOJIBAKE_MARKERS = ["繧", "縺", "譁", "蜩", "荳", "�"]


def text_targets() -> list[Path]:
    targets: list[Path] = []
    for pattern in ("*.md", "*.html"):
        for path in ROOT.rglob(pattern):
            relative_parts = path.relative_to(ROOT).parts
            if any(part in EXCLUDED_DIRS for part in relative_parts):
                continue
            targets.append(path)
    return sorted(targets)


def main() -> None:
    rows = [["path", "status", "chars", "mojibake_marker_count"]]
    failed = False
    for path in text_targets():
        try:
            text = path.read_text(encoding="utf-8")
            marker_count = sum(text.count(marker) for marker in MOJIBAKE_MARKERS)
            status = "ok" if marker_count == 0 else "suspect_mojibake"
            count = len(text)
        except UnicodeDecodeError:
            status = "decode_error"
            count = 0
            marker_count = 0
        if status != "ok":
            failed = True
        rows.append([str(path.relative_to(ROOT)), status, str(count), str(marker_count)])

    output = CASE_ROOT / "reports" / "encoding_check.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    print(output)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
