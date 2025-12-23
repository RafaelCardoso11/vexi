# Graphics bytecode namespace: 0x20
BASE = 0x20

OPS = {
    BASE + 0x10: "CREATE_SHAPE",
    BASE + 0x11: "UPDATE_COLOR",
    BASE + 0x12: "UPDATE_SHAPE",
    BASE + 0x13: "ROTATE",
    BASE + 0x14: "SCALE",
    BASE + 0x15: "TRANSLATE",
}

SHAPE_TYPES = {
    BASE + 0x00: "SQUARE",
    BASE + 0x01: "TRIANGLE",
    BASE + 0x02: "CIRCLE",
}

COLORS = {
    BASE + 0x01: [0x00, 0xFF, 0x00],  # red
    BASE + 0x02: [0xFF, 0x00, 0x00],  # green
    BASE + 0x03: [0x00, 0x00, 0xFF],  # blue
}

TOOLS = {
    "ops": OPS,
    "shape_types": SHAPE_TYPES,
    "colors": COLORS,
}
