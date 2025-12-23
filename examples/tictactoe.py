from vvm import VVMInstance as V
v=V()
def p(b):
 s={0:" ",1:"X",2:"O"};d="-------------";print(d);[print(f"| {s[b[i]]} | {s[b[i+1]]} | {s[b[i+2]]} |\n{d}") for i in (0,3,6)]
def c(v):
 for l in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]:
  a,b,c=l;[v.exec_patch(p) for p in [(98,('board',a,'var_i')),(98,('board',b,'var_x')),(98,('board',c,'var_y')),(33,('var_z','var_i',0)),(32,('var_temp','var_i','var_x')),(38,('var_z','var_z','var_temp')),(32,('var_temp','var_i','var_y')),(38,('var_z','var_z','var_temp'))]]
  if v.variables['var_z']==1:return v.variables['var_i']
 return 0
v.exec_patch((80,('board',9,0)));v.variables['p']=1;print("--- Tic-Tac-Toe ---")
for _ in range(9):
 p(v.variables['board']);pl=v.variables.get('p',1)
 while 1:
  try:
   m=int(input(f"Player {pl}(0-8):"));
   if 0<=m<=8 and v.variables['board'][m]==0:break
   else:print("Invalid move")
  except:print("Invalid input")
 v.exec_patch((99,('board',m,pl)));w=c(v)
 if w:p(v.variables['board']);print(f"P{w} wins!");break
 v.variables['p']=3-pl
else:p(v.variables['board']);print("Draw!")
