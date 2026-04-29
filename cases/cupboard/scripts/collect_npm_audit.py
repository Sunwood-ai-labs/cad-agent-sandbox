from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        "npm audit --json",
        cwd=ROOT,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=300,
    )
    raw_path = REPORTS / "npm_audit.json"
    raw_path.write_text(result.stdout or "{}", encoding="utf-8")
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    counts = payload.get("metadata", {}).get("vulnerabilities", {})
    total = counts.get("total", 0)
    rows = ["severity,count"]
    for severity in ["info", "low", "moderate", "high", "critical", "total"]:
        rows.append(f"{severity},{counts.get(severity, 0)}")
    (REPORTS / "npm_audit_summary.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"npm audit total={total} returncode={result.returncode}")


if __name__ == "__main__":
    main()

