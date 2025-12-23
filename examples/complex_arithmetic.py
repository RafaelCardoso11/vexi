from vvm import VVMInstance

vvm = VVMInstance()

# Opcodes
VAR_I = 0x30
VAR_X = 0x31
VAR_Y = 0x32
VAR_Z = 0x33
VAR_MOV = 0x35

ADD = 0x10
SUB = 0x11
MUL = 0x12
DIV = 0x13
MOD = 0x14

patches = [
    # Initialize variables
    (VAR_X, 100),   # var_x = 100
    (VAR_Y, 25),    # var_y = 25
    (VAR_Z, 0),     # var_z = 0

    # var_z = var_x + var_y (100 + 25 = 125)
    (VAR_MOV, ('var_z', 'var_x')),
    (ADD, ('var_z', 'var_y')),

    # var_z = var_z * 2 (125 * 2 = 250)
    (MUL, ('var_z', 2)),

    # var_z = var_z / var_y (250 / 25 = 10)
    (DIV, ('var_z', 'var_y')),

    # var_x = var_z - 5 (10 - 5 = 5)
    (VAR_MOV, ('var_x', 'var_z')),
    (SUB, ('var_x', 5)),

    # var_y = var_y % 3 (25 % 3 = 1)
    # The MOD operation modifies the destination, so we need a temp var
    (VAR_MOV, ('var_temp', 'var_y')),
    (MOD, ('var_temp', 3)),
    (VAR_MOV, ('var_y', 'var_temp')),
]

# Execute patches
for patch in patches:
    vvm.exec_patch(patch)

print("--- Complex Arithmetic Example ---")
print(f"var_x expected: 5, got: {vvm.variables['var_x']}")
print(f"var_y expected: 1, got: {vvm.variables['var_y']}")
print(f"var_z expected: 10, got: {vvm.variables['var_z']}")
print("------------------------------------")
