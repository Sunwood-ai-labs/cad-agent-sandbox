from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.exports import render_preview_png, write_manifest
from cupboard_benchmark.spec import cupboard_parts


OUT = ROOT / "outputs" / "forgecad"
SOURCE = ROOT / "designs" / "cupboard.forge.js"


def run(command: list[str], *, required: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        subprocess.list2cmdline(command),
        cwd=ROOT,
        shell=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=300,
    )
    if required and result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def uv_path() -> str | None:
    return shutil.which("uv")


def python_path() -> Path:
    return ROOT / ".venv" / "Scripts" / "python.exe"


def chrome_path() -> Path | None:
    candidates = [
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stl_path = OUT / "cupboard.stl"
    obj_path = OUT / "cupboard.obj"
    step_path = OUT / "cupboard.step"
    three_mf_path = OUT / "cupboard.3mf"
    screenshot_path = OUT / "cupboard_screenshot.png"
    preview_path = OUT / "cupboard_preview.png"
    run_log_path = OUT / "forgecad_run.txt"
    render_log_path = OUT / "forgecad_render.txt"
    step_probe_path = OUT / "forgecad_step_probe.txt"

    for generated_path in [screenshot_path, step_path]:
        if generated_path.exists():
            generated_path.unlink()

    run_result = run(["npx", "forgecad", "run", str(SOURCE)])
    run_log_path.write_text(run_result.stdout + "\n" + run_result.stderr, encoding="utf-8")

    run(["npx", "forgecad", "export", "stl", str(SOURCE), "--output", str(stl_path), "--quality", "high"])
    run(["npx", "forgecad", "export", "3mf", str(SOURCE), "--output", str(three_mf_path), "--quality", "high"])
    render_command = [
        "npx",
        "forgecad",
        "render",
        "3d",
        str(SOURCE),
        str(screenshot_path),
        "--camera",
        "iso",
        "--size",
        "1400",
        "--edges",
        "thin",
    ]
    chrome = chrome_path()
    if chrome:
        render_command.extend(["--chrome-path", str(chrome)])
    render_result = run(render_command, required=False)
    render_log_path.write_text(
        "COMMAND: " + " ".join(render_command) + "\n"
        + f"RETURNCODE: {render_result.returncode}\n"
        + "STDOUT:\n"
        + render_result.stdout
        + "\nSTDERR:\n"
        + render_result.stderr,
        encoding="utf-8",
    )
    generated_screenshot = render_result.returncode == 0 and screenshot_path.exists() and screenshot_path.stat().st_size > 0

    generated_step = False
    step_command = [
        "npx",
        "forgecad",
        "export",
        "step",
        str(SOURCE),
        "--output",
        str(step_path),
        "--allow-faceted",
    ]
    if python_path().exists():
        step_command.extend(["--python", str(python_path())])
    uv = uv_path()
    if uv:
        step_command.extend(["--uv", uv])
    step_result = run(step_command, required=False)
    step_probe_path.write_text(
        "COMMAND: " + " ".join(step_command) + "\n"
        + f"RETURNCODE: {step_result.returncode}\n"
        + "STDOUT:\n"
        + step_result.stdout
        + "\nSTDERR:\n"
        + step_result.stderr,
        encoding="utf-8",
    )
    if step_result.returncode == 0 and step_path.exists() and step_path.stat().st_size > 0:
        generated_step = True

    try:
        import trimesh

        mesh = trimesh.load(stl_path, force="mesh")
        mesh.export(obj_path)
    except Exception as exc:
        (OUT / "obj_conversion_error.txt").write_text(str(exc), encoding="utf-8")

    render_preview_png(cupboard_parts(), preview_path, "ForgeCAD cupboard benchmark")

    step_note = "STEP was attempted with --allow-faceted and local uv/Python."
    if not generated_step and "Pro" in (step_result.stderr or ""):
        step_note = "STEP export was attempted but ForgeCAD reported that export step requires a Pro license."

    render_note = "ForgeCAD render 3d completed."
    if not generated_screenshot:
        render_note = "ForgeCAD render 3d was attempted but did not complete; shared preview PNG is used for reports."

    write_manifest(
        "ForgeCAD",
        OUT,
        {
            "source": str(SOURCE.relative_to(ROOT)),
            "step": str(step_path.relative_to(ROOT)) if generated_step else None,
            "stl": str(stl_path.relative_to(ROOT)) if stl_path.exists() else None,
            "obj": str(obj_path.relative_to(ROOT)) if obj_path.exists() else None,
            "preview": str(preview_path.relative_to(ROOT)),
            "screenshot": str(screenshot_path.relative_to(ROOT)) if generated_screenshot else None,
            "3mf": str(three_mf_path.relative_to(ROOT)) if three_mf_path.exists() else None,
            "run_log": str(run_log_path.relative_to(ROOT)),
            "render_log": str(render_log_path.relative_to(ROOT)),
            "step_probe": str(step_probe_path.relative_to(ROOT)),
        },
        [
            "ForgeCAD CLI was installed as a local npm dev dependency.",
            "STL and 3MF were exported with ForgeCAD CLI.",
            render_note,
            "OBJ was converted from ForgeCAD STL using trimesh.",
            step_note,
        ],
    )


if __name__ == "__main__":
    main()
