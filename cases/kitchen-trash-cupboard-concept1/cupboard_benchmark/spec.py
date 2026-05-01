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
COUNTER_Z = 876.0
COUNTER_TOP_Z = COUNTER_Z + COUNTER
WORK_COUNTER_DEPTH = 450.0

LOWER_CLEAR_Z = TOE_KICK_HEIGHT + PANEL
LOWER_FRONT_RAIL_HEIGHT = 28.0
DUST_SPACE_WIDTH = 520.0
DUST_SPACE_DEPTH = 600.0
DUST_SPACE_HEIGHT = COUNTER_Z - LOWER_FRONT_RAIL_HEIGHT - LOWER_CLEAR_Z
TRASH_BAY_COLUMNS = 3
TRASH_BIN_WIDTH = 440.0
TRASH_BIN_DEPTH = 500.0
TRASH_BIN_HEIGHT = 620.0

UPPER_DEPTH = 290.0
UPPER_FRONT_Y = DEPTH - UPPER_DEPTH
UPPER_START_Z = 1260.0
UPPER_INNER_HEIGHT = TOTAL_HEIGHT - UPPER_START_Z - 2 * PANEL
PEGBOARD_Z = COUNTER_TOP_Z + 10.0
PEGBOARD_HEIGHT = UPPER_START_Z - PEGBOARD_Z

WOOD = (205, 171, 116)
WOOD_LIGHT = (222, 186, 132)
EDGE = (172, 132, 82)
BACK_COLOR = (176, 185, 179)
DOOR_COLOR = (230, 214, 181)
DOOR_SHADOW = (46, 42, 36)
PLINTH_COLOR = (78, 73, 67)
SHELF_COLOR = (214, 185, 131)
PEGBOARD_COLOR = (197, 154, 99)
PEG_HOLE_COLOR = (52, 42, 32)
OUTLET_COLOR = (232, 226, 208)
METAL = (118, 122, 121)
GLASS_DARK = (42, 45, 47)
CREAM = (232, 224, 206)
WHITE = (238, 236, 228)
LEAF_GREEN = (72, 126, 67)
TOWEL = (214, 205, 190)
TOWEL_STRIPE = (141, 132, 116)
BIN_COLORS = [(150, 171, 139), (111, 146, 171), (162, 162, 158)]
BIN_LID_COLOR = (207, 211, 209)
BIN_LABEL = (244, 246, 240)


def _add(
    parts: list[BoxPart],
    name: str,
    role: str,
    x: float,
    y: float,
    z: float,
    dx: float,
    dy: float,
    dz: float,
    color: tuple[int, int, int],
) -> None:
    parts.append(BoxPart(name, role, x, y, z, dx, dy, dz, color))


def _add_peg_holes(parts: list[BoxPart]) -> None:
    hole_size = 7.0
    y = DEPTH - BACK - 4.0
    columns = [180.0 + index * 100.0 for index in range(14)]
    rows = [950.0 + index * 48.0 for index in range(6)]
    for row_index, z in enumerate(rows, start=1):
        for col_index, x in enumerate(columns, start=1):
            if 1180.0 <= x <= 1450.0 and 1040.0 <= z <= 1145.0:
                continue
            _add(
                parts,
                f"peg_hole_{row_index:02d}_{col_index:02d}",
                "peg_hole",
                x,
                y,
                z,
                hole_size,
                4.0,
                hole_size,
                PEG_HOLE_COLOR,
            )


def _add_bin_label(parts: list[BoxPart], index: int, x: float, y: float, z: float) -> None:
    label_x = x + TRASH_BIN_WIDTH / 2 - 48.0
    label_y = y - 8.0
    label_z = z + 250.0
    _add(parts, f"trash_bin_{index}_front_label", "bin_label", label_x, label_y, label_z, 96.0, 8.0, 58.0, BIN_LABEL)
    _add(parts, f"trash_bin_{index}_icon_top", "bin_label", label_x + 32.0, label_y - 4.0, label_z + 42.0, 32.0, 4.0, 5.0, METAL)
    _add(parts, f"trash_bin_{index}_icon_left", "bin_label", label_x + 24.0, label_y - 4.0, label_z + 18.0, 6.0, 4.0, 22.0, METAL)
    _add(parts, f"trash_bin_{index}_icon_right", "bin_label", label_x + 66.0, label_y - 4.0, label_z + 18.0, 6.0, 4.0, 22.0, METAL)


def _add_counter_objects(parts: list[BoxPart]) -> None:
    base_z = COUNTER_TOP_Z

    # Toaster group.
    _add(parts, "toaster_body", "counter_appliance", 70.0, 52.0, base_z, 300.0, 210.0, 150.0, CREAM)
    _add(parts, "toaster_window", "counter_appliance", 118.0, 46.0, base_z + 44.0, 204.0, 6.0, 70.0, GLASS_DARK)
    _add(parts, "toaster_top_slot", "counter_appliance", 138.0, 92.0, base_z + 150.0, 160.0, 44.0, 7.0, GLASS_DARK)
    _add(parts, "toaster_left_knob", "counter_appliance", 104.0, 44.0, base_z + 16.0, 26.0, 6.0, 26.0, METAL)
    _add(parts, "toaster_right_knob", "counter_appliance", 300.0, 44.0, base_z + 16.0, 26.0, 6.0, 26.0, METAL)

    # Kettle and morning drink set.
    _add(parts, "kettle_body", "counter_appliance", 500.0, 92.0, base_z, 118.0, 120.0, 160.0, WHITE)
    _add(parts, "kettle_spout", "counter_appliance", 618.0, 112.0, base_z + 82.0, 34.0, 46.0, 34.0, WHITE)
    _add(parts, "kettle_handle", "counter_appliance", 484.0, 118.0, base_z + 55.0, 16.0, 70.0, 86.0, METAL)
    _add(parts, "tall_glass", "counter_decor", 1040.0, 118.0, base_z, 42.0, 42.0, 118.0, (206, 216, 214))
    _add(parts, "white_mug", "counter_decor", 1108.0, 112.0, base_z, 58.0, 58.0, 72.0, WHITE)
    _add(parts, "mug_handle", "counter_decor", 1166.0, 126.0, base_z + 20.0, 12.0, 30.0, 36.0, WHITE)

    # Plant.
    _add(parts, "plant_pot", "counter_decor", 795.0, 112.0, base_z, 88.0, 88.0, 78.0, (180, 160, 128))
    for index, (x, y, dz) in enumerate(
        [
            (805.0, 124.0, 86.0),
            (828.0, 105.0, 104.0),
            (854.0, 126.0, 88.0),
            (818.0, 154.0, 76.0),
            (846.0, 152.0, 92.0),
        ],
        start=1,
    ):
        _add(parts, f"plant_leaf_{index}", "counter_decor", x, y, base_z + 78.0, 18.0, 8.0, dz, LEAF_GREEN)


def _add_outlet_and_towel(parts: list[BoxPart]) -> None:
    plate_x = 1215.0
    plate_y = DEPTH - BACK - 8.0
    plate_z = 1082.0
    _add(parts, "sliding_outlet_plate", "outlet", plate_x, plate_y, plate_z, 175.0, 4.0, 48.0, OUTLET_COLOR)
    _add(parts, "outlet_left_socket", "outlet", plate_x + 42.0, plate_y - 2.0, plate_z + 14.0, 28.0, 2.0, 20.0, METAL)
    _add(parts, "outlet_right_socket", "outlet", plate_x + 103.0, plate_y - 2.0, plate_z + 14.0, 28.0, 2.0, 20.0, METAL)
    _add(parts, "outlet_slide_cover", "outlet", plate_x + 132.0, plate_y - 3.0, plate_z + 6.0, 32.0, 3.0, 36.0, (196, 185, 166))

    _add(parts, "peg_hook_bar", "towel", 1490.0, DEPTH - BACK - 12.0, 1068.0, 92.0, 6.0, 12.0, METAL)
    _add(parts, "hanging_towel_body", "towel", 1512.0, DEPTH - BACK - 24.0, 900.0, 64.0, 10.0, 212.0, TOWEL)
    for index, z in enumerate([940.0, 996.0, 1052.0], start=1):
        _add(parts, f"hanging_towel_stripe_{index}", "towel", 1512.0, DEPTH - BACK - 26.0, z, 64.0, 2.0, 7.0, TOWEL_STRIPE)


def cupboard_parts() -> list[BoxPart]:
    inner_width = WIDTH - 2 * PANEL
    parts: list[BoxPart] = []

    # Lower full-depth carcass and counter deck.
    _add(parts, "lower_left_side", "carcass", 0, 0, TOE_KICK_HEIGHT, PANEL, DEPTH, COUNTER_TOP_Z - TOE_KICK_HEIGHT, WOOD)
    _add(parts, "lower_right_side", "carcass", WIDTH - PANEL, 0, TOE_KICK_HEIGHT, PANEL, DEPTH, COUNTER_TOP_Z - TOE_KICK_HEIGHT, WOOD)
    _add(parts, "bottom_deck", "carcass", PANEL, 0, TOE_KICK_HEIGHT, inner_width, DEPTH, PANEL, EDGE)
    _add(parts, "trash_counter_deck", "counter", PANEL, 0, COUNTER_Z, inner_width, WORK_COUNTER_DEPTH, COUNTER, EDGE)
    _add(parts, "lower_back_panel", "carcass", PANEL, DEPTH - BACK, LOWER_CLEAR_Z, inner_width, BACK, COUNTER_Z - LOWER_CLEAR_Z, BACK_COLOR)
    _add(parts, "lower_rear_rail", "carcass", PANEL, DEPTH - BACK - PANEL, LOWER_CLEAR_Z, inner_width, PANEL, 80.0, EDGE)
    _add(parts, "lower_front_rail", "carcass", PANEL, 0, COUNTER_Z - LOWER_FRONT_RAIL_HEIGHT, inner_width, 18.0, LOWER_FRONT_RAIL_HEIGHT, EDGE)

    used_bay_width = TRASH_BAY_COLUMNS * DUST_SPACE_WIDTH + 2 * PANEL
    bay_start_x = (WIDTH - used_bay_width) / 2
    for index, divider_x in enumerate([bay_start_x + DUST_SPACE_WIDTH, bay_start_x + DUST_SPACE_WIDTH * 2 + PANEL], start=1):
        _add(
            parts,
            f"trash_bay_divider_{index}",
            "divider",
            divider_x,
            24.0,
            LOWER_CLEAR_Z,
            PANEL,
            DUST_SPACE_DEPTH,
            DUST_SPACE_HEIGHT,
            WOOD,
        )

    # Recessed base and adjustable-feet hint.
    _add(parts, "recessed_toe_kick", "toe_kick", 90.0, 58.0, 0.0, WIDTH - 180.0, PANEL, TOE_KICK_HEIGHT, PLINTH_COLOR)
    for index, x in enumerate([140.0, WIDTH - 190.0], start=1):
        _add(parts, f"adjuster_foot_{index}", "toe_kick", x, 590.0, 0.0, 34.0, 34.0, 20.0, PLINTH_COLOR)

    # Three open trash bins, matching the concept order: green, blue, gray.
    for index in range(TRASH_BAY_COLUMNS):
        compartment_x = bay_start_x + index * (DUST_SPACE_WIDTH + PANEL)
        bin_x = compartment_x + (DUST_SPACE_WIDTH - TRASH_BIN_WIDTH) / 2
        bin_y = 60.0
        bin_z = LOWER_CLEAR_Z + 20.0
        _add(parts, f"trash_bin_{index + 1}", "trash_bin", bin_x, bin_y, bin_z, TRASH_BIN_WIDTH, TRASH_BIN_DEPTH, TRASH_BIN_HEIGHT, BIN_COLORS[index])
        _add(parts, f"trash_bin_{index + 1}_lid", "trash_lid", bin_x, bin_y, bin_z + TRASH_BIN_HEIGHT, TRASH_BIN_WIDTH, TRASH_BIN_DEPTH, PANEL, BIN_LID_COLOR)
        _add(parts, f"trash_bin_{index + 1}_front_lip", "trash_lid", bin_x, bin_y - 16.0, bin_z + TRASH_BIN_HEIGHT, TRASH_BIN_WIDTH, 16.0, PANEL, BIN_LID_COLOR)
        _add_bin_label(parts, index + 1, bin_x, bin_y, bin_z)

    # Open morning workflow deck: pegboard, outlet, appliances, and hanging cloth.
    _add(parts, "middle_pegboard", "pegboard", PANEL, DEPTH - BACK, PEGBOARD_Z, inner_width, BACK, PEGBOARD_HEIGHT, PEGBOARD_COLOR)
    _add_peg_holes(parts)
    _add_counter_objects(parts)
    _add_outlet_and_towel(parts)

    # Shallow upper storage set back to respect the D290 concept note.
    upper_inner_depth = UPPER_DEPTH - BACK
    upper_inner_z = UPPER_START_Z + PANEL
    upper_inner_height = TOTAL_HEIGHT - UPPER_START_Z - 2 * PANEL
    upper_center_x = WIDTH / 2 - PANEL / 2
    left_upper_width = upper_center_x - PANEL
    right_upper_x = upper_center_x + PANEL
    right_upper_width = WIDTH - PANEL - right_upper_x

    _add(parts, "upper_left_side", "carcass", 0, UPPER_FRONT_Y, UPPER_START_Z, PANEL, UPPER_DEPTH, TOTAL_HEIGHT - UPPER_START_Z, WOOD)
    _add(parts, "upper_right_side", "carcass", WIDTH - PANEL, UPPER_FRONT_Y, UPPER_START_Z, PANEL, UPPER_DEPTH, TOTAL_HEIGHT - UPPER_START_Z, WOOD)
    _add(parts, "upper_bottom_panel", "carcass", PANEL, UPPER_FRONT_Y, UPPER_START_Z, inner_width, UPPER_DEPTH, PANEL, EDGE)
    _add(parts, "top_panel", "carcass", PANEL, UPPER_FRONT_Y, TOTAL_HEIGHT - PANEL, inner_width, UPPER_DEPTH, PANEL, EDGE)
    _add(
        parts,
        "upper_back_panel",
        "carcass",
        PANEL,
        UPPER_FRONT_Y + UPPER_DEPTH - BACK,
        upper_inner_z,
        inner_width,
        BACK,
        upper_inner_height,
        BACK_COLOR,
    )
    _add(parts, "upper_center_divider", "divider", upper_center_x, UPPER_FRONT_Y, upper_inner_z, PANEL, upper_inner_depth, upper_inner_height, WOOD)

    for index, z in enumerate([1428.0, 1608.0], start=1):
        _add(parts, f"left_adjustable_shelf_{index}", "shelf", PANEL, UPPER_FRONT_Y + 12.0, z, left_upper_width, upper_inner_depth - 18.0, PANEL, SHELF_COLOR)
        _add(parts, f"right_adjustable_shelf_{index}", "shelf", right_upper_x, UPPER_FRONT_Y + 12.0, z, right_upper_width, upper_inner_depth - 18.0, PANEL, SHELF_COLOR)

    door_width = (WIDTH - 3 * DOOR_GAP) / 2
    door_height = TOTAL_HEIGHT - UPPER_START_Z - PANEL - 2 * DOOR_GAP
    door_z = UPPER_START_Z + PANEL + DOOR_GAP
    door_y = UPPER_FRONT_Y - DOOR
    detail_y = door_y - 2.0
    _add(parts, "upper_left_door", "door", DOOR_GAP, door_y, door_z, door_width, DOOR, door_height, DOOR_COLOR)
    _add(parts, "upper_right_door", "door", 2 * DOOR_GAP + door_width, door_y, door_z, door_width, DOOR, door_height, DOOR_COLOR)
    _add(parts, "upper_door_center_reveal", "door_detail", WIDTH / 2 - 1.5, detail_y, door_z, 3.0, 2.0, door_height, DOOR_SHADOW)
    _add(parts, "upper_left_bottom_pull_shadow", "door_detail", 90.0, detail_y, UPPER_START_Z + 8.0, 600.0, 2.0, 5.0, DOOR_SHADOW)
    _add(parts, "upper_right_bottom_pull_shadow", "door_detail", 990.0, detail_y, UPPER_START_Z + 8.0, 600.0, 2.0, 5.0, DOOR_SHADOW)

    return parts


def expected_metrics() -> dict[str, object]:
    parts = cupboard_parts()
    inner_width = WIDTH - 2 * PANEL
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
        "overall_size_note": "Matches W1680 x D650 x H1800 concept envelope with a shallow D290 upper cabinet.",
        "inner_width": inner_width,
        "inner_depth": DEPTH - BACK,
        "inner_height": CARCASS_HEIGHT - PANEL,
        "upper_storage_inner_depth": UPPER_DEPTH - BACK,
        "upper_storage_inner_height": UPPER_INNER_HEIGHT,
        "upper_front_y": UPPER_FRONT_Y,
        "upper_door_y": UPPER_FRONT_Y - DOOR,
        "upper_back_y": UPPER_FRONT_Y + UPPER_DEPTH - BACK,
        "counter_top_height": COUNTER_TOP_Z,
        "counter_depth": WORK_COUNTER_DEPTH,
        "pegboard_y": DEPTH - BACK,
        "pegboard_size": [inner_width, BACK, PEGBOARD_HEIGHT],
        "trash_bay_columns": TRASH_BAY_COLUMNS,
        "trash_bay_clear_width_each": DUST_SPACE_WIDTH,
        "trash_bay_clear_depth": DUST_SPACE_DEPTH,
        "trash_bay_clear_height": DUST_SPACE_HEIGHT,
        "trash_bin_size": [TRASH_BIN_WIDTH, TRASH_BIN_DEPTH, TRASH_BIN_HEIGHT],
        "panel_thickness": PANEL,
        "back_thickness": BACK,
        "door_thickness": DOOR,
        "part_count": len(parts),
        "role_counts": role_counts,
    }
