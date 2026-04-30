const { cuboid } = require('@jscad/modeling').primitives
const { translate } = require('@jscad/modeling').transforms
const { union } = require('@jscad/modeling').booleans

const parts = [
  {
    "name": "left_side",
    "role": "carcass",
    "pos": [
      0,
      0,
      90.0
    ],
    "size": [
      18.0,
      650.0,
      1710.0
    ]
  },
  {
    "name": "right_side",
    "role": "carcass",
    "pos": [
      1662.0,
      0,
      90.0
    ],
    "size": [
      18.0,
      650.0,
      1710.0
    ]
  },
  {
    "name": "bottom_deck",
    "role": "carcass",
    "pos": [
      18.0,
      0,
      90.0
    ],
    "size": [
      1644.0,
      650.0,
      18.0
    ]
  },
  {
    "name": "trash_counter_deck",
    "role": "carcass",
    "pos": [
      18.0,
      0,
      820.0
    ],
    "size": [
      1644.0,
      650.0,
      24.0
    ]
  },
  {
    "name": "top_panel",
    "role": "carcass",
    "pos": [
      18.0,
      0,
      1782.0
    ],
    "size": [
      1644.0,
      650.0,
      18.0
    ]
  },
  {
    "name": "upper_back_panel",
    "role": "carcass",
    "pos": [
      18.0,
      644.0,
      844.0
    ],
    "size": [
      1644.0,
      6.0,
      938.0
    ]
  },
  {
    "name": "lower_rear_rail",
    "role": "carcass",
    "pos": [
      18.0,
      632.0,
      108.0
    ],
    "size": [
      1644.0,
      18,
      80
    ]
  },
  {
    "name": "lower_front_rail",
    "role": "carcass",
    "pos": [
      18.0,
      0,
      790.0
    ],
    "size": [
      1644.0,
      18,
      30.0
    ]
  },
  {
    "name": "trash_bay_divider_1",
    "role": "divider",
    "pos": [
      554.0,
      24,
      108.0
    ],
    "size": [
      18.0,
      590.0,
      682.0
    ]
  },
  {
    "name": "trash_bay_divider_2",
    "role": "divider",
    "pos": [
      1108.0,
      24,
      108.0
    ],
    "size": [
      18.0,
      590.0,
      682.0
    ]
  },
  {
    "name": "upper_center_divider",
    "role": "divider",
    "pos": [
      831.0,
      0,
      844.0
    ],
    "size": [
      18.0,
      626.0,
      938.0
    ]
  },
  {
    "name": "left_adjustable_shelf_1",
    "role": "shelf",
    "pos": [
      18.0,
      0,
      1162.92
    ],
    "size": [
      813.0,
      626.0,
      18.0
    ]
  },
  {
    "name": "right_adjustable_shelf_1",
    "role": "shelf",
    "pos": [
      849.0,
      0,
      1162.92
    ],
    "size": [
      813.0,
      626.0,
      18.0
    ]
  },
  {
    "name": "left_adjustable_shelf_2",
    "role": "shelf",
    "pos": [
      18.0,
      0,
      1481.8400000000001
    ],
    "size": [
      813.0,
      626.0,
      18.0
    ]
  },
  {
    "name": "right_adjustable_shelf_2",
    "role": "shelf",
    "pos": [
      849.0,
      0,
      1481.8400000000001
    ],
    "size": [
      813.0,
      626.0,
      18.0
    ]
  },
  {
    "name": "trash_bin_1",
    "role": "trash_bin",
    "pos": [
      66.0,
      70.0,
      126.0
    ],
    "size": [
      440.0,
      500.0,
      620.0
    ]
  },
  {
    "name": "trash_bin_1_lid",
    "role": "trash_lid",
    "pos": [
      66.0,
      70.0,
      746.0
    ],
    "size": [
      440.0,
      500.0,
      18.0
    ]
  },
  {
    "name": "trash_bin_2",
    "role": "trash_bin",
    "pos": [
      620.0,
      70.0,
      126.0
    ],
    "size": [
      440.0,
      500.0,
      620.0
    ]
  },
  {
    "name": "trash_bin_2_lid",
    "role": "trash_lid",
    "pos": [
      620.0,
      70.0,
      746.0
    ],
    "size": [
      440.0,
      500.0,
      18.0
    ]
  },
  {
    "name": "trash_bin_3",
    "role": "trash_bin",
    "pos": [
      1174.0,
      70.0,
      126.0
    ],
    "size": [
      440.0,
      500.0,
      620.0
    ]
  },
  {
    "name": "trash_bin_3_lid",
    "role": "trash_lid",
    "pos": [
      1174.0,
      70.0,
      746.0
    ],
    "size": [
      440.0,
      500.0,
      18.0
    ]
  },
  {
    "name": "upper_left_door",
    "role": "door",
    "pos": [
      3.0,
      -16.0,
      847.0
    ],
    "size": [
      835.5,
      16.0,
      950.0
    ]
  },
  {
    "name": "upper_right_door",
    "role": "door",
    "pos": [
      841.5,
      -16.0,
      847.0
    ],
    "size": [
      835.5,
      16.0,
      950.0
    ]
  },
  {
    "name": "left_handle",
    "role": "handle",
    "pos": [
      786.0,
      -48.0,
      1158.0
    ],
    "size": [
      18.0,
      32.0,
      360.0
    ]
  },
  {
    "name": "right_handle",
    "role": "handle",
    "pos": [
      876.0,
      -48.0,
      1158.0
    ],
    "size": [
      18.0,
      32.0,
      360.0
    ]
  },
  {
    "name": "recessed_toe_kick",
    "role": "toe_kick",
    "pos": [
      90,
      58,
      0
    ],
    "size": [
      1500.0,
      18.0,
      90.0
    ]
  }
]

const boxPart = (part) => {
  const center = [
    part.pos[0] + part.size[0] / 2,
    part.pos[1] + part.size[1] / 2,
    part.pos[2] + part.size[2] / 2
  ]
  return translate(center, cuboid({ size: part.size }))
}

const main = () => union(parts.map(boxPart))

module.exports = { main, parts }
