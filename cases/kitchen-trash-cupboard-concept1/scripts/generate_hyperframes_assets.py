from __future__ import annotations

import csv
import json
import shutil
import sys
import urllib.request
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cupboard_benchmark.spec import BoxPart
from cupboard_benchmark.spec import cupboard_parts
from cupboard_benchmark.spec import expected_metrics


VIDEO = ROOT / "videos" / "kitchen-trash-cupboard-comparison"
ASSETS = VIDEO / "assets"
VIEWS = ROOT / "reports" / "video_views"
ICON_URL = "https://pbs.twimg.com/profile_images/1599014676909522944/UNh8fZEr_400x400.png"
METHODS = ["cadquery", "build123d", "jscad", "openscad", "forgecad"]
METHOD_LABELS = {
    "cadquery": "CadQuery",
    "build123d": "build123d",
    "jscad": "JSCAD",
    "openscad": "OpenSCAD",
    "forgecad": "ForgeCAD CLI",
}
VIEW_LABELS = {
    "front": "正面",
    "side": "側面",
    "top": "上面",
}


def font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/yugothb.ttc"),
        Path("C:/Windows/Fonts/meiryob.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_leaf(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float, color: tuple[int, int, int, int]) -> None:
    stem = [(x, y + int(80 * scale)), (x + int(40 * scale), y + int(5 * scale))]
    draw.line(stem, fill=color, width=max(1, int(4 * scale)))
    for index in range(5):
        ox = int((index * 8 - 16) * scale)
        oy = int((62 - index * 13) * scale)
        rx = int((18 - index) * scale)
        ry = int((9 + index) * scale)
        draw.ellipse((x + ox - rx, y + oy - ry, x + ox + rx, y + oy + ry), fill=color)


def bounds(parts: list[BoxPart], axes: tuple[str, str]) -> tuple[float, float, float, float]:
    values: list[tuple[float, float]] = []
    for part in parts:
        mins = {"x": part.x, "y": part.y, "z": part.z}
        maxs = {"x": part.x + part.dx, "y": part.y + part.dy, "z": part.z + part.dz}
        values.append((mins[axes[0]], mins[axes[1]]))
        values.append((maxs[axes[0]], maxs[axes[1]]))
    xs = [value[0] for value in values]
    ys = [value[1] for value in values]
    return min(xs), max(xs), min(ys), max(ys)


def part_rect(part: BoxPart, axes: tuple[str, str]) -> tuple[float, float, float, float]:
    mins = {"x": part.x, "y": part.y, "z": part.z}
    maxs = {"x": part.x + part.dx, "y": part.y + part.dy, "z": part.z + part.dz}
    return mins[axes[0]], mins[axes[1]], maxs[axes[0]], maxs[axes[1]]


def depth_key(part: BoxPart, view: str) -> float:
    if view == "front":
        return -(part.y + part.dy)
    if view == "side":
        return part.x
    return part.z


def render_view(method: str, view: str, output: Path) -> None:
    parts = cupboard_parts()
    axes_by_view = {
        "front": ("x", "z"),
        "side": ("y", "z"),
        "top": ("x", "y"),
    }
    axes = axes_by_view[view]
    min_a, max_a, min_b, max_b = bounds(parts, axes)
    width, height = 1280, 920
    margin_left, margin_top = 118, 116
    margin_right, margin_bottom = 88, 112
    scale = min(
        (width - margin_left - margin_right) / (max_a - min_a),
        (height - margin_top - margin_bottom) / (max_b - min_b),
    )
    canvas = Image.new("RGBA", (width, height), (247, 246, 239, 255))
    draw = ImageDraw.Draw(canvas, "RGBA")

    draw.rectangle((0, 0, width, height), fill=(247, 246, 239, 255))
    draw_leaf(draw, 38, 24, 0.72, (97, 128, 93, 62))
    draw_leaf(draw, width - 126, height - 122, 0.68, (130, 151, 88, 46))
    draw.text((56, 42), METHOD_LABELS[method], fill=(41, 55, 42, 255), font=font(34))
    draw.text((56, 80), f"共通仕様 {VIEW_LABELS[view]}ガイド | ゴミ箱3台対応", fill=(92, 103, 86, 255), font=font(20))

    def screen(a: float, b: float) -> tuple[float, float]:
        sx = margin_left + (a - min_a) * scale
        sy = height - margin_bottom - (b - min_b) * scale
        return sx, sy

    for part in sorted(parts, key=lambda item: depth_key(item, view)):
        a0, b0, a1, b1 = part_rect(part, axes)
        x0, y1 = screen(a0, b0)
        x1, y0 = screen(a1, b1)
        fill = tuple(list(part.color) + [218])
        outline = (56, 64, 53, 185)
        draw.rounded_rectangle((x0, y0, x1, y1), radius=3, fill=fill, outline=outline, width=2)

    draw.line((margin_left, height - margin_bottom + 22, width - margin_right, height - margin_bottom + 22), fill=(122, 134, 105, 120), width=2)
    metrics = expected_metrics()
    draw.text(
        (56, height - 58),
        f"{metrics['carcass_width']:.0f}W x {metrics['carcass_depth']:.0f}D x {metrics['total_height']:.0f}H mm | 3 trash-bin lower bay",
        fill=(82, 91, 76, 255),
        font=font(18),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=96)


def copy_screenshots() -> None:
    (ASSETS / "screenshots").mkdir(parents=True, exist_ok=True)
    for method in METHODS:
        source = ROOT / "reports" / "screenshots" / f"{method}.png"
        target = ASSETS / "screenshots" / f"{method}.png"
        shutil.copy2(source, target)


def generate_views() -> None:
    (ASSETS / "views").mkdir(parents=True, exist_ok=True)
    VIEWS.mkdir(parents=True, exist_ok=True)
    for method in METHODS:
        for view in VIEW_LABELS:
            report_path = VIEWS / f"{method}_{view}.png"
            render_view(method, view, report_path)
            shutil.copy2(report_path, ASSETS / "views" / report_path.name)


def download_icon() -> None:
    output = ASSETS / "sunwood_icon.png"
    if output.exists() and output.stat().st_size > 0:
        return
    try:
        with urllib.request.urlopen(ICON_URL, timeout=30) as response:
            output.write_bytes(response.read())
    except Exception:
        image = Image.new("RGBA", (400, 400), (236, 242, 226, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        draw.ellipse((36, 36, 364, 364), fill=(86, 122, 84, 255))
        draw.text((118, 174), "SW", fill=(247, 246, 239, 255), font=font(76))
        image.save(output)


def read_measurements() -> list[dict[str, str]]:
    with (ROOT / "reports" / "measurements.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_video_data() -> None:
    rows = read_measurements()
    payload = {
        "methods": [
            {
                "id": row["method"].lower().replace(" cli", "").replace(" ", ""),
                "label": row["method"],
                "score": row["score"],
                "step": row["step"],
                "stl": row["stl"],
                "obj": row["obj"],
                "png": row["preview"],
                "bbox": row["bbox_pass"],
                "volume": row["volume_pass"],
                "watertight": row["watertight_any"],
            }
            for row in rows
        ],
        "icon_url": ICON_URL,
        "footer": "Maki@Sunwood AI Labs.",
    }
    (ASSETS / "video-data.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    copy_screenshots()
    generate_views()
    download_icon()
    write_video_data()
    print(ASSETS)


if __name__ == "__main__":
    main()
