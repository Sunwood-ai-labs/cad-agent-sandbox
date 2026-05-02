from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".tmp_markdown_link_check.csv"
EXCLUDED_DIRS = {".git", ".venv", "node_modules", "tools", "outputs", "renders", "qa_frames"}
ROOT_UNTRACKED_DOCS = {"README.md", "README.ja.md", "CONTRIBUTING.md", "SECURITY.md"}


def git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def candidate_markdown_files() -> list[Path]:
    paths = set(git_lines(["ls-files", "*.md"]))
    for relative in git_lines(["ls-files", "--others", "--exclude-standard", "*.md"]):
        path = Path(relative)
        if path.parts and path.parts[0] in {".github", "docs", "scripts"}:
            paths.add(relative)
        elif relative in ROOT_UNTRACKED_DOCS:
            paths.add(relative)
    return sorted((ROOT / path).resolve() for path in paths)


def is_external(link: str) -> bool:
    parsed = urlparse(link)
    return parsed.scheme in {"http", "https", "mailto"}


def is_excluded(path: Path) -> bool:
    try:
        parts = path.relative_to(ROOT).parts
    except ValueError:
        return False
    return any(part in EXCLUDED_DIRS for part in parts)


def main() -> None:
    rows = [["source", "path", "status", "target"]]
    failed = False
    for markdown_file in candidate_markdown_files():
        if is_excluded(markdown_file) or not markdown_file.exists():
            continue
        text = markdown_file.read_text(encoding="utf-8")
        source = str(markdown_file.relative_to(ROOT))
        links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)
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
            if target.exists():
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
