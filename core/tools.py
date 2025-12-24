# -------------------------------
# Base offset for bytecode
# -------------------------------
BASE = 0x00

# -------------------------------
# Arithmetic operations
# -------------------------------
ARITHMETIC_OPS = {
    BASE + 0x10: "ADD",   # addition
    BASE + 0x11: "SUB",   # subtraction
    BASE + 0x12: "MUL",   # multiplication
    BASE + 0x13: "DIV",   # division
    BASE + 0x14: "MOD",   # modulo
}

# -------------------------------
# Logic operations
# -------------------------------
LOGIC_OPS = {
    BASE + 0x20: "EQ",    # ==
    BASE + 0x21: "NEQ",   # !=
    BASE + 0x22: "GT",    # >
    BASE + 0x23: "LT",    # <
    BASE + 0x24: "GTE",   # >=
    BASE + 0x25: "LTE",   # <=
    BASE + 0x26: "AND",   # &&
    BASE + 0x27: "OR",    # ||
    BASE + 0x28: "NOT",   # !
}

# -------------------------------
# Variables
# -------------------------------
VARIABLES = {
    BASE + 0x30: "var_i",      # generic counter
    BASE + 0x31: "var_x",      # generic numeric
    BASE + 0x32: "var_y",
    BASE + 0x33: "var_z",
    BASE + 0x34: "var_temp",   # temporary variable
    BASE + 0x35: "var_mov",    # move/copy variable
}

# -------------------------------
# Control flow
# -------------------------------
CONTROL = {
    BASE + 0x40: "IF",
    BASE + 0x41: "ELSE",
    BASE + 0x42: "WHILE",
    BASE + 0x43: "FOR",
    BASE + 0x44: "BREAK",
    BASE + 0x45: "CONTINUE",
    BASE + 0x46: "SWITCH",
    BASE + 0x47: "CASE",
}

# -------------------------------
# Constants (literals)
# -------------------------------
CONSTANTS = {i: i for i in range(256)}

EXTRA_CONSTANTS = {
    BASE + 0xF0: 0.0,
    BASE + 0xF1: 1.0,
    BASE + 0xF2: True,
    BASE + 0xF3: False,
}

# -------------------------------
# Data structures
# -------------------------------
DATA_STRUCTURES = {
    BASE + 0x50: "ARRAY",  # arrays only (lists)
}

DS_OPERATIONS = {
    BASE + 0x60: "PUSH",
    BASE + 0x61: "POP",
    BASE + 0x62: "GET",
    BASE + 0x63: "SET",
    BASE + 0x64: "LENGTH",
}

# -------------------------------
# I/O Operations
# -------------------------------
IO_OPS = {
    BASE + 0x70: "PRINT_STR", # Print a string literal
    BASE + 0x71: "PRINT_VAR", # Print a variable's value
    BASE + 0x72: "INPUT_INT", # Read integer input into a variable
}

# -------------------------------
# Control Flow Operations
# -------------------------------
CONTROL_FLOW_OPS = {
    BASE + 0x80: "LABEL",      # Pseudo-op for marking a line
    BASE + 0x81: "JMP",        # Unconditional jump
    BASE + 0x82: "JMP_IF_EQ",  # Jump if equal
    BASE + 0x83: "JMP_IF_NEQ", # Jump if not equal
}


# -------------------------------
# Unified tools dictionary
# -------------------------------
TOOLS = {
    "arithmetic": ARITHMETIC_OPS,
    "logic": LOGIC_OPS,
    "variables": VARIABLES,
    "control": CONTROL,
    "data_structures": DATA_STRUCTURES,
    "ds_operations": DS_OPERATIONS,
    "io": IO_OPS,
    "control_flow": CONTROL_FLOW_OPS,
    "constants": CONSTANTS,
    "extra_constants": EXTRA_CONSTANTS,
}
