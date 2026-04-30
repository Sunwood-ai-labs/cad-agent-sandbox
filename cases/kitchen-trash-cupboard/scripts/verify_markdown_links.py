from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlparse


CASE_ROOT = Path(__file__).resolve().parents[1]
ROOT = CASE_ROOT.parents[1]
EXCLUDED_DIRS = {".venv", "node_modules", "tools"}
OUTPUT = CASE_ROOT / "reports" / "markdown_link_check.csv"


def markdown_targets() -> list[Path]:
    targets: list[Path] = []
    for path in ROOT.rglob("*.md"):
        relative_parts = path.relative_to(ROOT).parts
        if any(part in EXCLUDED_DIRS for part in relative_parts):
            continue
        targets.append(path)
    return sorted(targets)


def is_external(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "mailto"}


def main() -> None:
    rows = [["source", "path", "status", "target"]]
    failed = False
    for markdown_file in markdown_targets():
        text = markdown_file.read_text(encoding="utf-8")
        links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)
        source = str(markdown_file.relative_to(ROOT))
        for link in links:
            if is_external(link):
                rows.append([source, link, "external", ""])
                continue
            target_text = link.split("#", 1)[0]
            if not target_text:
                rows.append([source, link, "anchor_only", ""])
                continue
            target = (markdown_file.parent / unquote(target_text)).resolve()
            try:
                relative_target = str(target.relative_to(ROOT))
            except ValueError:
                relative_target = str(target)
            if target == OUTPUT.resolve() or target.exists():
                rows.append([source, link, "ok", relative_target])
            else:
                rows.append([source, link, "missing", relative_target])
                failed = True

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)
    print(OUTPUT)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
