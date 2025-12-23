from vvm import VVMInstance
v=VVMInstance()
p=[(0x30,0),(0x31,0)]
for i in range(1,6):p+=[(0x30,i),(0x10,('var_x','var_i'))]
for i in p:v.exec_patch(i)
print("Sum from 1 to 5:",v.variables['var_x'])
