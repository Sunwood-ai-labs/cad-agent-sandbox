from __future__ import annotations

from .spec import BoxPart


def overlap_volume(a: BoxPart, b: BoxPart) -> float:
    ax0, ay0, az0 = a.min_corner
    ax1, ay1, az1 = a.max_corner
    bx0, by0, bz0 = b.min_corner
    bx1, by1, bz1 = b.max_corner
    ox = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    oy = max(0.0, min(ay1, by1) - max(ay0, by0))
    oz = max(0.0, min(az1, bz1) - max(az0, bz0))
    return ox * oy * oz


def positive_overlap_pairs(parts: list[BoxPart]) -> list[tuple[str, str, float]]:
    overlaps = []
    for index, first in enumerate(parts):
        for second in parts[index + 1 :]:
            volume = overlap_volume(first, second)
            if volume > 1e-6:
                overlaps.append((first.name, second.name, volume))
    return overlaps
