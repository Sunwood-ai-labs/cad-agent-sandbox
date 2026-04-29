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
      100.0
    ],
    "size": [
      18.0,
      450.0,
      1900.0
    ]
  },
  {
    "name": "right_side",
    "role": "carcass",
    "pos": [
      882.0,
      0,
      100.0
    ],
    "size": [
      18.0,
      450.0,
      1900.0
    ]
  },
  {
    "name": "bottom_panel",
    "role": "carcass",
    "pos": [
      18.0,
      0,
      100.0
    ],
    "size": [
      864.0,
      450.0,
      18.0
    ]
  },
  {
    "name": "top_panel",
    "role": "carcass",
    "pos": [
      18.0,
      0,
      1982.0
    ],
    "size": [
      864.0,
      450.0,
      18.0
    ]
  },
  {
    "name": "back_panel",
    "role": "carcass",
    "pos": [
      18.0,
      444.0,
      118.0
    ],
    "size": [
      864.0,
      6.0,
      1864.0
    ]
  },
  {
    "name": "adjustable_shelf_1",
    "role": "shelf",
    "pos": [
      18.0,
      0,
      584.0
    ],
    "size": [
      864.0,
      444.0,
      18.0
    ]
  },
  {
    "name": "adjustable_shelf_2",
    "role": "shelf",
    "pos": [
      18.0,
      0,
      1050.0
    ],
    "size": [
      864.0,
      444.0,
      18.0
    ]
  },
  {
    "name": "adjustable_shelf_3",
    "role": "shelf",
    "pos": [
      18.0,
      0,
      1516.0
    ],
    "size": [
      864.0,
      444.0,
      18.0
    ]
  },
  {
    "name": "left_door",
    "role": "door",
    "pos": [
      3.0,
      -16.0,
      103.0
    ],
    "size": [
      445.5,
      16.0,
      1894.0
    ]
  },
  {
    "name": "right_door",
    "role": "door",
    "pos": [
      451.5,
      -16.0,
      103.0
    ],
    "size": [
      445.5,
      16.0,
      1894.0
    ]
  },
  {
    "name": "left_handle",
    "role": "handle",
    "pos": [
      408.0,
      -34.0,
      928.0
    ],
    "size": [
      18.0,
      18.0,
      320.0
    ]
  },
  {
    "name": "right_handle",
    "role": "handle",
    "pos": [
      474.0,
      -34.0,
      928.0
    ],
    "size": [
      18.0,
      18.0,
      320.0
    ]
  },
  {
    "name": "recessed_toe_kick",
    "role": "toe_kick",
    "pos": [
      60,
      42,
      0
    ],
    "size": [
      780.0,
      18.0,
      100.0
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
