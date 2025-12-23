from vvm import VVMInstance

vvm = VVMInstance()
patches = [
    (0x30, 0),
    (0x31, 0),
]
for i in range(1, 6):
    patches.append((0x30, i))
    patches.append((0x10, ('var_x', 'var_i')))
for patch in patches:
    vvm.exec_patch(patch)
print("Sum from 1 to 5:", vvm.variables["var_x"])
