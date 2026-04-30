from __future__ import annotations

import csv
from datetime import datetime
from datetime import timezone
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
RESULT = REPORTS / "run_all_last_result.csv"

COMMANDS = [
    [sys.executable, "scripts/generate_cadquery.py"],
    [sys.executable, "scripts/generate_build123d.py"],
    [sys.executable, "scripts/generate_openscad.py"],
    [sys.executable, "scripts/generate_jscad_source.py"],
    ["npm", "run", "generate:jscad"],
    [sys.executable, "scripts/finalize_jscad.py"],
    [sys.executable, "scripts/generate_forgecad_source.py"],
    [sys.executable, "scripts/generate_forgecad.py"],
    [sys.executable, "scripts/collect_screenshots.py"],
    [sys.executable, "scripts/collect_npm_audit.py"],
    [sys.executable, "scripts/score_outputs.py"],
    [sys.executable, "scripts/verify_step_imports.py"],
    [sys.executable, "scripts/verify_openscad_step_probe.py"],
    [sys.executable, "scripts/verify_text_encoding.py"],
    [sys.executable, "scripts/verify_report_images.py"],
    [sys.executable, "scripts/verify_markdown_links.py"],
]


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    if os.name == "nt" and command[0] in {"npm", "npx"}:
        subprocess.run(subprocess.list2cmdline(command), cwd=ROOT, check=True, shell=True)
    else:
        subprocess.run(command, cwd=ROOT, check=True)


def write_result(status: str, returncode: int, failed_command: str, completed_steps: int) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp_utc", "status", "returncode", "failed_command", "completed_steps", "total_steps"])
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                status,
                returncode,
                failed_command,
                completed_steps,
                len(COMMANDS),
            ]
        )
    print(RESULT)


def main() -> None:
    completed_steps = 0
    try:
        for command in COMMANDS:
            run(command)
            completed_steps += 1
    except subprocess.CalledProcessError as exc:
        failed_command = " ".join(str(part) for part in exc.cmd) if isinstance(exc.cmd, list) else str(exc.cmd)
        write_result("failed", exc.returncode, failed_command, completed_steps)
        raise
    write_result("ok", 0, "", completed_steps)


if __name__ == "__main__":
    main()
