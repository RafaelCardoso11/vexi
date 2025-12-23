from vvm import VVMInstance
v=VVMInstance()
p=[(0x31,100),(0x32,25),(0x33,0),(0x35,('var_z','var_x')),(0x10,('var_z','var_y')),(0x12,('var_z',2)),(0x13,('var_z','var_y')),(0x35,('var_x','var_z')),(0x11,('var_x',5)),(0x35,('var_temp','var_y')),(0x14,('var_temp',3)),(0x35,('var_y','var_temp'))]
for i in p:v.exec_patch(i)
print("--- Complex Arithmetic Example ---")
print(f"x: 5, got: {v.variables['var_x']}")
print(f"y: 1, got: {v.variables['var_y']}")
print(f"z: 10, got: {v.variables['var_z']}")
print("------------------------------------")
