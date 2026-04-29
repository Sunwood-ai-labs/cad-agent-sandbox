from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BoxPart:
    name: str
    role: str
    x: float
    y: float
    z: float
    dx: float
    dy: float
    dz: float
    color: tuple[int, int, int]

    @property
    def center(self) -> tuple[float, float, float]:
        return (self.x + self.dx / 2, self.y + self.dy / 2, self.z + self.dz / 2)

    @property
    def min_corner(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @property
    def max_corner(self) -> tuple[float, float, float]:
        return (self.x + self.dx, self.y + self.dy, self.z + self.dz)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["center"] = self.center
        return data


WIDTH = 900.0
DEPTH = 450.0
TOTAL_HEIGHT = 2000.0
TOE_KICK_HEIGHT = 100.0
CARCASS_HEIGHT = TOTAL_HEIGHT - TOE_KICK_HEIGHT

PANEL = 18.0
BACK = 6.0
DOOR = 16.0
DOOR_GAP = 3.0
HANDLE_WIDTH = 18.0
HANDLE_DEPTH = 18.0
HANDLE_HEIGHT = 320.0

WOOD = (205, 171, 116)
EDGE = (172, 132, 82)
BACK_COLOR = (176, 185, 179)
DOOR_COLOR = (230, 214, 181)
HANDLE_COLOR = (46, 49, 52)
PLINTH_COLOR = (78, 73, 67)
SHELF_COLOR = (214, 185, 131)


def cupboard_parts() -> list[BoxPart]:
    inner_width = WIDTH - 2 * PANEL
    inner_depth = DEPTH - BACK
    inner_height = CARCASS_HEIGHT - 2 * PANEL
    shelf_zs = [
        TOE_KICK_HEIGHT + PANEL + inner_height * 0.25,
        TOE_KICK_HEIGHT + PANEL + inner_height * 0.50,
        TOE_KICK_HEIGHT + PANEL + inner_height * 0.75,
    ]
    door_width = (WIDTH - 3 * DOOR_GAP) / 2
    door_height = CARCASS_HEIGHT - 2 * DOOR_GAP
    handle_z = TOE_KICK_HEIGHT + CARCASS_HEIGHT * 0.52 - HANDLE_HEIGHT / 2

    parts = [
        BoxPart("left_side", "carcass", 0, 0, TOE_KICK_HEIGHT, PANEL, DEPTH, CARCASS_HEIGHT, WOOD),
        BoxPart("right_side", "carcass", WIDTH - PANEL, 0, TOE_KICK_HEIGHT, PANEL, DEPTH, CARCASS_HEIGHT, WOOD),
        BoxPart("bottom_panel", "carcass", PANEL, 0, TOE_KICK_HEIGHT, inner_width, DEPTH, PANEL, EDGE),
        BoxPart("top_panel", "carcass", PANEL, 0, TOTAL_HEIGHT - PANEL, inner_width, DEPTH, PANEL, EDGE),
        BoxPart(
            "back_panel",
            "carcass",
            PANEL,
            DEPTH - BACK,
            TOE_KICK_HEIGHT + PANEL,
            inner_width,
            BACK,
            CARCASS_HEIGHT - 2 * PANEL,
            BACK_COLOR,
        ),
    ]

    for index, z in enumerate(shelf_zs, start=1):
        parts.append(
            BoxPart(
                f"adjustable_shelf_{index}",
                "shelf",
                PANEL,
                0,
                z,
                inner_width,
                inner_depth,
                PANEL,
                SHELF_COLOR,
            )
        )

    parts.extend(
        [
            BoxPart(
                "left_door",
                "door",
                DOOR_GAP,
                -DOOR,
                TOE_KICK_HEIGHT + DOOR_GAP,
                door_width,
                DOOR,
                door_height,
                DOOR_COLOR,
            ),
            BoxPart(
                "right_door",
                "door",
                2 * DOOR_GAP + door_width,
                -DOOR,
                TOE_KICK_HEIGHT + DOOR_GAP,
                door_width,
                DOOR,
                door_height,
                DOOR_COLOR,
            ),
            BoxPart(
                "left_handle",
                "handle",
                WIDTH / 2 - 42,
                -DOOR - HANDLE_DEPTH,
                handle_z,
                HANDLE_WIDTH,
                HANDLE_DEPTH,
                HANDLE_HEIGHT,
                HANDLE_COLOR,
            ),
            BoxPart(
                "right_handle",
                "handle",
                WIDTH / 2 + 24,
                -DOOR - HANDLE_DEPTH,
                handle_z,
                HANDLE_WIDTH,
                HANDLE_DEPTH,
                HANDLE_HEIGHT,
                HANDLE_COLOR,
            ),
            BoxPart(
                "recessed_toe_kick",
                "toe_kick",
                60,
                42,
                0,
                WIDTH - 120,
                PANEL,
                TOE_KICK_HEIGHT,
                PLINTH_COLOR,
            ),
        ]
    )
    return parts


def expected_metrics() -> dict[str, object]:
    parts = cupboard_parts()
    min_x = min(part.x for part in parts)
    min_y = min(part.y for part in parts)
    min_z = min(part.z for part in parts)
    max_x = max(part.x + part.dx for part in parts)
    max_y = max(part.y + part.dy for part in parts)
    max_z = max(part.z + part.dz for part in parts)
    role_counts: dict[str, int] = {}
    for part in parts:
        role_counts[part.role] = role_counts.get(part.role, 0) + 1
    return {
        "carcass_width": WIDTH,
        "carcass_depth": DEPTH,
        "total_height": TOTAL_HEIGHT,
        "carcass_size_without_front_hardware": [WIDTH, DEPTH, TOTAL_HEIGHT],
        "overall_bbox": [min_x, min_y, min_z, max_x, max_y, max_z],
        "overall_size": [max_x - min_x, max_y - min_y, max_z - min_z],
        "overall_size_note": "Includes front door and handle protrusion; carcass depth itself is 450 mm.",
        "inner_width": WIDTH - 2 * PANEL,
        "inner_depth": DEPTH - BACK,
        "inner_height": CARCASS_HEIGHT - 2 * PANEL,
        "panel_thickness": PANEL,
        "back_thickness": BACK,
        "door_thickness": DOOR,
        "part_count": len(parts),
        "role_counts": role_counts,
    }
