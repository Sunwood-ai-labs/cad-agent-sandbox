// Cupboard benchmark generated for ForgeCAD CLI.
// Units: millimeters. Coordinate system: X width, Y depth, Z up.

const parts = [
  {
    "name": "left_side",
    "role": "carcass",
    "position": [
      9.0,
      225.0,
      100.0
    ],
    "size": [
      18.0,
      450.0,
      1900.0
    ],
    "color": "#cdab74"
  },
  {
    "name": "right_side",
    "role": "carcass",
    "position": [
      891.0,
      225.0,
      100.0
    ],
    "size": [
      18.0,
      450.0,
      1900.0
    ],
    "color": "#cdab74"
  },
  {
    "name": "bottom_panel",
    "role": "carcass",
    "position": [
      450.0,
      225.0,
      100.0
    ],
    "size": [
      864.0,
      450.0,
      18.0
    ],
    "color": "#ac8452"
  },
  {
    "name": "top_panel",
    "role": "carcass",
    "position": [
      450.0,
      225.0,
      1982.0
    ],
    "size": [
      864.0,
      450.0,
      18.0
    ],
    "color": "#ac8452"
  },
  {
    "name": "back_panel",
    "role": "carcass",
    "position": [
      450.0,
      447.0,
      118.0
    ],
    "size": [
      864.0,
      6.0,
      1864.0
    ],
    "color": "#b0b9b3"
  },
  {
    "name": "adjustable_shelf_1",
    "role": "shelf",
    "position": [
      450.0,
      222.0,
      584.0
    ],
    "size": [
      864.0,
      444.0,
      18.0
    ],
    "color": "#d6b983"
  },
  {
    "name": "adjustable_shelf_2",
    "role": "shelf",
    "position": [
      450.0,
      222.0,
      1050.0
    ],
    "size": [
      864.0,
      444.0,
      18.0
    ],
    "color": "#d6b983"
  },
  {
    "name": "adjustable_shelf_3",
    "role": "shelf",
    "position": [
      450.0,
      222.0,
      1516.0
    ],
    "size": [
      864.0,
      444.0,
      18.0
    ],
    "color": "#d6b983"
  },
  {
    "name": "left_door",
    "role": "door",
    "position": [
      225.75,
      -8.0,
      103.0
    ],
    "size": [
      445.5,
      16.0,
      1894.0
    ],
    "color": "#e6d6b5"
  },
  {
    "name": "right_door",
    "role": "door",
    "position": [
      674.25,
      -8.0,
      103.0
    ],
    "size": [
      445.5,
      16.0,
      1894.0
    ],
    "color": "#e6d6b5"
  },
  {
    "name": "left_handle",
    "role": "handle",
    "position": [
      417.0,
      -25.0,
      928.0
    ],
    "size": [
      18.0,
      18.0,
      320.0
    ],
    "color": "#2e3134"
  },
  {
    "name": "right_handle",
    "role": "handle",
    "position": [
      483.0,
      -25.0,
      928.0
    ],
    "size": [
      18.0,
      18.0,
      320.0
    ],
    "color": "#2e3134"
  },
  {
    "name": "recessed_toe_kick",
    "role": "toe_kick",
    "position": [
      450.0,
      51.0,
      0
    ],
    "size": [
      780.0,
      18.0,
      100.0
    ],
    "color": "#4e4943"
  }
];

return parts.map((part) => ({
  name: part.name,
  shape: box(part.size[0], part.size[1], part.size[2])
    .translate(part.position[0], part.position[1], part.position[2])
    .color(part.color),
}));
