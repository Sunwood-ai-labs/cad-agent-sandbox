from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw

from .spec import BoxPart, cupboard_parts, expected_metrics


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def part_vertices(part: BoxPart) -> list[tuple[float, float, float]]:
    x0, y0, z0 = part.min_corner
    x1, y1, z1 = part.max_corner
    return [
        (x0, y0, z0),
        (x1, y0, z0),
        (x1, y1, z0),
        (x0, y1, z0),
        (x0, y0, z1),
        (x1, y0, z1),
        (x1, y1, z1),
        (x0, y1, z1),
    ]


BOX_FACES = [
    (0, 1, 2, 3),
    (4, 7, 6, 5),
    (0, 4, 5, 1),
    (1, 5, 6, 2),
    (2, 6, 7, 3),
    (3, 7, 4, 0),
]

TRIANGLES = [
    (0, 1, 2),
    (0, 2, 3),
    (4, 7, 6),
    (4, 6, 5),
    (0, 4, 5),
    (0, 5, 1),
    (1, 5, 6),
    (1, 6, 2),
    (2, 6, 7),
    (2, 7, 3),
    (3, 7, 4),
    (3, 4, 0),
]


def write_obj(parts: Iterable[BoxPart], output_path: Path) -> None:
    ensure_dir(output_path.parent)
    lines = ["# Cupboard benchmark OBJ", "mtllib cupboard.mtl"]
    vertex_offset = 1
    material_lines = []
    for part in parts:
        r, g, b = [channel / 255 for channel in part.color]
        material_lines.extend(
            [
                f"newmtl {part.name}",
                f"Kd {r:.4f} {g:.4f} {b:.4f}",
                "Ka 0.0000 0.0000 0.0000",
                "Ks 0.1000 0.1000 0.1000",
                "",
            ]
        )
        lines.append(f"o {part.name}")
        lines.append(f"usemtl {part.name}")
        for vertex in part_vertices(part):
            lines.append(f"v {vertex[0]:.4f} {vertex[1]:.4f} {vertex[2]:.4f}")
        for face in BOX_FACES:
            indices = [str(vertex_offset + idx) for idx in face]
            lines.append("f " + " ".join(indices))
        vertex_offset += 8
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output_path.with_suffix(".mtl").write_text("\n".join(material_lines), encoding="utf-8")


def _normal(a: tuple[float, float, float], b: tuple[float, float, float], c: tuple[float, float, float]) -> tuple[float, float, float]:
    ux, uy, uz = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    vx, vy, vz = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return (nx / length, ny / length, nz / length)


def write_ascii_stl(parts: Iterable[BoxPart], output_path: Path, solid_name: str) -> None:
    ensure_dir(output_path.parent)
    lines = [f"solid {solid_name}"]
    for part in parts:
        vertices = part_vertices(part)
        for tri in TRIANGLES:
            a, b, c = [vertices[index] for index in tri]
            nx, ny, nz = _normal(a, b, c)
            lines.append(f"  facet normal {nx:.6f} {ny:.6f} {nz:.6f}")
            lines.append("    outer loop")
            for vertex in (a, b, c):
                lines.append(f"      vertex {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}")
            lines.append("    endloop")
            lines.append("  endfacet")
    lines.append(f"endsolid {solid_name}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _project(point: tuple[float, float, float]) -> tuple[float, float]:
    x, y, z = point
    return ((x - y) * 0.86, -z - (x + y) * 0.28)


def _shade(color: tuple[int, int, int], factor: float) -> tuple[int, int, int, int]:
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
        230,
    )


def render_preview_png(parts: Iterable[BoxPart], output_path: Path, title: str) -> None:
    ensure_dir(output_path.parent)
    parts = list(parts)
    faces = []
    for part in parts:
        vertices = part_vertices(part)
        visible_faces = [
            ((4, 7, 6, 5), 1.10),
            ((0, 4, 5, 1), 0.96),
            ((3, 7, 4, 0), 0.84),
            ((1, 5, 6, 2), 0.76),
        ]
        for face, factor in visible_faces:
            points = [vertices[index] for index in face]
            depth = sum(point[0] + point[1] - point[2] * 0.2 for point in points) / 4
            faces.append((depth, [_project(point) for point in points], _shade(part.color, factor), part.name))
    all_points = [point for _, polygon, _, _ in faces for point in polygon]
    min_x = min(point[0] for point in all_points)
    max_x = max(point[0] for point in all_points)
    min_y = min(point[1] for point in all_points)
    max_y = max(point[1] for point in all_points)
    width, height = 1400, 1200
    margin = 90
    scale = min((width - 2 * margin) / (max_x - min_x), (height - 2 * margin) / (max_y - min_y))

    def screen(point: tuple[float, float]) -> tuple[float, float]:
        return ((point[0] - min_x) * scale + margin, (point[1] - min_y) * scale + margin)

    image = Image.new("RGBA", (width, height), (248, 248, 245, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    for _, polygon, color, _ in sorted(faces, key=lambda item: item[0], reverse=True):
        draw.polygon([screen(point) for point in polygon], fill=color, outline=(54, 54, 54, 180))
    draw.text((32, 28), title, fill=(25, 25, 25, 255))
    draw.text(
        (32, height - 54),
        "1680W x 650D x 1800H mm | concept preview, not structural signoff",
        fill=(70, 70, 70, 255),
    )
    image.convert("RGB").save(output_path)


def write_manifest(method: str, output_dir: Path, generated_files: dict[str, str | None], notes: list[str]) -> None:
    ensure_dir(output_dir)
    payload = {
        "method": method,
        "spec": expected_metrics(),
        "parts": [part.to_dict() for part in cupboard_parts()],
        "generated_files": generated_files,
        "notes": notes,
    }
    (output_dir / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_parts_csv(output_path: Path) -> None:
    ensure_dir(output_path.parent)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["name", "role", "x", "y", "z", "dx", "dy", "dz"])
        for part in cupboard_parts():
            writer.writerow([part.name, part.role, part.x, part.y, part.z, part.dx, part.dy, part.dz])
