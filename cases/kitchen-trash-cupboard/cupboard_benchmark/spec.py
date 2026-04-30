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


WIDTH = 1680.0
DEPTH = 650.0
TOTAL_HEIGHT = 1800.0
TOE_KICK_HEIGHT = 90.0
CARCASS_HEIGHT = TOTAL_HEIGHT - TOE_KICK_HEIGHT

PANEL = 18.0
BACK = 6.0
DOOR = 16.0
DOOR_GAP = 3.0
COUNTER = 24.0
COUNTER_Z = 820.0
LOWER_CLEAR_Z = TOE_KICK_HEIGHT + PANEL
LOWER_CLEAR_HEIGHT = COUNTER_Z - LOWER_CLEAR_Z
TRASH_BIN_WIDTH = 440.0
TRASH_BIN_DEPTH = 500.0
TRASH_BIN_HEIGHT = 620.0
TRASH_BAY_COLUMNS = 3
HANDLE_WIDTH = 18.0
HANDLE_DEPTH = 32.0
HANDLE_HEIGHT = 360.0

WOOD = (205, 171, 116)
EDGE = (172, 132, 82)
BACK_COLOR = (176, 185, 179)
DOOR_COLOR = (230, 214, 181)
HANDLE_COLOR = (46, 49, 52)
PLINTH_COLOR = (78, 73, 67)
SHELF_COLOR = (214, 185, 131)
BIN_COLORS = [(104, 124, 130), (95, 132, 108), (126, 122, 108)]
BIN_LID_COLOR = (58, 69, 74)


def cupboard_parts() -> list[BoxPart]:
    inner_width = WIDTH - 2 * PANEL
    upper_depth = DEPTH - BACK
    upper_start = COUNTER_Z + COUNTER
    upper_height = TOTAL_HEIGHT - upper_start - PANEL
    shelf_zs = [upper_start + upper_height * 0.34, upper_start + upper_height * 0.68]
    door_width = (WIDTH - 3 * DOOR_GAP) / 2
    door_height = TOTAL_HEIGHT - upper_start - 2 * DOOR_GAP
    handle_z = upper_start + door_height * 0.52 - HANDLE_HEIGHT / 2
    lower_opening_depth = DEPTH - 60
    lower_front_rail_height = 30.0
    divider_width = PANEL
    clear_bin_bay_width = (inner_width - 2 * divider_width) / TRASH_BAY_COLUMNS

    parts = [
        BoxPart("left_side", "carcass", 0, 0, TOE_KICK_HEIGHT, PANEL, DEPTH, CARCASS_HEIGHT, WOOD),
        BoxPart("right_side", "carcass", WIDTH - PANEL, 0, TOE_KICK_HEIGHT, PANEL, DEPTH, CARCASS_HEIGHT, WOOD),
        BoxPart("bottom_deck", "carcass", PANEL, 0, TOE_KICK_HEIGHT, inner_width, DEPTH, PANEL, EDGE),
        BoxPart("trash_counter_deck", "carcass", PANEL, 0, COUNTER_Z, inner_width, DEPTH, COUNTER, EDGE),
        BoxPart("top_panel", "carcass", PANEL, 0, TOTAL_HEIGHT - PANEL, inner_width, DEPTH, PANEL, EDGE),
        BoxPart(
            "upper_back_panel",
            "carcass",
            PANEL,
            DEPTH - BACK,
            upper_start,
            inner_width,
            BACK,
            TOTAL_HEIGHT - upper_start - PANEL,
            BACK_COLOR,
        ),
        BoxPart("lower_rear_rail", "carcass", PANEL, DEPTH - 18, LOWER_CLEAR_Z, inner_width, 18, 80, EDGE),
        BoxPart(
            "lower_front_rail",
            "carcass",
            PANEL,
            0,
            COUNTER_Z - lower_front_rail_height,
            inner_width,
            18,
            lower_front_rail_height,
            EDGE,
        ),
    ]

    for index, divider_x in enumerate(
        [
            PANEL + clear_bin_bay_width,
            PANEL + clear_bin_bay_width * 2 + divider_width,
        ],
        start=1,
    ):
        parts.append(
            BoxPart(
                f"trash_bay_divider_{index}",
                "divider",
                divider_x,
                24,
                LOWER_CLEAR_Z,
                divider_width,
                lower_opening_depth,
                COUNTER_Z - LOWER_CLEAR_Z - lower_front_rail_height,
                WOOD,
            )
        )

    upper_divider_x = WIDTH / 2 - PANEL / 2
    parts.append(
        BoxPart(
            "upper_center_divider",
            "divider",
            upper_divider_x,
            0,
            upper_start,
            PANEL,
            upper_depth - 18,
            TOTAL_HEIGHT - upper_start - PANEL,
            WOOD,
        )
    )

    left_upper_width = upper_divider_x - PANEL
    right_upper_x = upper_divider_x + PANEL
    right_upper_width = WIDTH - PANEL - right_upper_x
    for index, z in enumerate(shelf_zs, start=1):
        parts.extend(
            [
                BoxPart(
                    f"left_adjustable_shelf_{index}",
                    "shelf",
                    PANEL,
                    0,
                    z,
                    left_upper_width,
                    upper_depth - 18,
                    PANEL,
                    SHELF_COLOR,
                ),
                BoxPart(
                    f"right_adjustable_shelf_{index}",
                    "shelf",
                    right_upper_x,
                    0,
                    z,
                    right_upper_width,
                    upper_depth - 18,
                    PANEL,
                    SHELF_COLOR,
                ),
            ]
        )

    for index in range(TRASH_BAY_COLUMNS):
        compartment_x = PANEL + index * (clear_bin_bay_width + divider_width)
        bin_x = compartment_x + (clear_bin_bay_width - TRASH_BIN_WIDTH) / 2
        bin_y = 70.0
        bin_z = LOWER_CLEAR_Z + 18.0
        parts.extend(
            [
                BoxPart(
                    f"trash_bin_{index + 1}",
                    "trash_bin",
                    bin_x,
                    bin_y,
                    bin_z,
                    TRASH_BIN_WIDTH,
                    TRASH_BIN_DEPTH,
                    TRASH_BIN_HEIGHT,
                    BIN_COLORS[index],
                ),
                BoxPart(
                    f"trash_bin_{index + 1}_lid",
                    "trash_lid",
                    bin_x,
                    bin_y,
                    bin_z + TRASH_BIN_HEIGHT,
                    TRASH_BIN_WIDTH,
                    TRASH_BIN_DEPTH,
                    PANEL,
                    BIN_LID_COLOR,
                ),
            ]
        )

    parts.extend(
        [
            BoxPart(
                "upper_left_door",
                "door",
                DOOR_GAP,
                -DOOR,
                upper_start + DOOR_GAP,
                door_width,
                DOOR,
                door_height,
                DOOR_COLOR,
            ),
            BoxPart(
                "upper_right_door",
                "door",
                2 * DOOR_GAP + door_width,
                -DOOR,
                upper_start + DOOR_GAP,
                door_width,
                DOOR,
                door_height,
                DOOR_COLOR,
            ),
            BoxPart(
                "left_handle",
                "handle",
                WIDTH / 2 - 54,
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
                WIDTH / 2 + 36,
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
                90,
                58,
                0,
                WIDTH - 180,
                PANEL,
                TOE_KICK_HEIGHT,
                PLINTH_COLOR,
            ),
        ]
    )
    return parts


def expected_metrics() -> dict[str, object]:
    parts = cupboard_parts()
    inner_width = WIDTH - 2 * PANEL
    clear_bin_bay_width = (inner_width - 2 * PANEL) / TRASH_BAY_COLUMNS
    lower_opening_depth = DEPTH - 60
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
        "overall_size_note": "Includes upper door and handle protrusion; carcass depth itself is 650 mm.",
        "inner_width": inner_width,
        "inner_depth": DEPTH - BACK,
        "inner_height": CARCASS_HEIGHT - PANEL,
        "trash_bay_columns": TRASH_BAY_COLUMNS,
        "trash_bay_clear_width_each": clear_bin_bay_width,
        "trash_bay_clear_depth": lower_opening_depth,
        "trash_bay_clear_height": LOWER_CLEAR_HEIGHT,
        "trash_bin_size": [TRASH_BIN_WIDTH, TRASH_BIN_DEPTH, TRASH_BIN_HEIGHT],
        "panel_thickness": PANEL,
        "back_thickness": BACK,
        "door_thickness": DOOR,
        "part_count": len(parts),
        "role_counts": role_counts,
    }
