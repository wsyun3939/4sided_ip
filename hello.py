import gurobipy as gp
from gurobipy import GRB

DEPTH=3
WIDTH=6
NBLOCK=15

#Sets
Width = range(WIDTH)
Depth = range(DEPTH)
Priority= range(NBLOCK)
Time= range(NBLOCK)

#Data
v=[]
for i in range(NBLOCK):
    row = []
    for j in range(NBLOCK):
        if j<=i:
            row.append(0)  # 初期化したい値を指定する
        else:
            row.append(1)
    v.append(row)

for row in v:
    for element in row:
        print(element, end=' ')
    print()

for row in Width:
    print(row, end=' ')
print()

for row in Depth:
    print(row, end=' ')
print()

for row in Priority:
    print(row, end=' ')
print()

for row in Time:
    print(row, end=' ')
print()


#Model
m = gp.Model("DBRP")
m.setParam(GRB.Param.LogToConsole, 1)
m.setParam(GRB.Param.OutputFlag, 1)

#Variables
x = { (i,j,k,l,n,t): m.addVar(vtype=GRB.BINARY) for i in Width for j in Depth for k in Width for l in Depth for n in Priority for t in Time}
y = { (i,j,n,t): m.addVar(vtype=GRB.BINARY) for i in Width for j in Depth for n in Priority for t in Time}
b = { (i,j,n,t): m.addVar(vtype=GRB.BINARY) for i in Width for j in Depth for n in Priority for t in Time}

#Objective (DBRP)
m.setObjective(gp.quicksum(x[i,j,k,l,n,t] for i in Width for j in Depth for k in Width for l in Depth for n in Priority for t in Time), GRB.MINIMIZE)


#Constraints
#(1)
for n in Priority:
    for t in Time:
        m.addConstr(gp.quicksum(b[i,j,n,t] for i in Width for j in Depth) + v[n][t] == 1)

#(2)
for i in Width:
    for j in Depth:
        for t in Time:
            m.addConstr(gp.quicksum(b[i,j,n,t] for n in Priority) <= 1)

#(3)
for i in Width:
    for j in Depth:
        if j == DEPTH-1:
            continue
        for t in Time:
            m.addConstr(gp.quicksum(b[i,j,n,t] for n in Priority) >= gp.quicksum(b[i,j+1,n,t] for n in Priority))

#(6)
for i in Width:
    for j in Depth:
        for n in Priority:
            for t in Time:
                if t == 0:
                    continue
                m.addConstr(b[i,j,n,t]==b[i,j,n,t-1]+gp.quicksum(x[k,l,i,j,n,t-1] for k in Width for l in Depth) - 
                            gp.quicksum(x[i,j,k,l,n,t-1] for k in Width for l in Depth) - y[i,j,n,t-1])
                
#(7)
for n in Priority:
    for t in Time:
        m.addConstr(v[n][t] == gp.quicksum(y[i,j,n,t_dash] for i in Width for j in Depth for t_dash in Time if t_dash < t))

#(8)
for i in Width:
    for k in Width:
        for j in Depth:
            for l in Depth:
                for t in Time:
                    if t==NBLOCK-1:
                        continue
                    m.addConstr(1-gp.quicksum(x[i,j,k,l,n,t] for n in Priority) >= gp.quicksum(x[i,j_dash,k,l_dash,n,t] for n in Priority for j_dash in Depth if j_dash > j for l_dash in Depth if l_dash > l))

#(9)
for i in Width:
    for t in Time:
        m.addConstr(100*(1-gp.quicksum(b[i,j,t,t] for j in Depth)) >= gp.quicksum(gp.quicksum(x[i_dash,j,k,l,n,t] for i_dash in Width if i_dash < i)+gp.quicksum(x[i_dash_dash,j,k,l,n,t] for i_dash_dash in Width if i_dash_dash > i) for j in Depth for k in Width for l in Depth for n in Priority))

#(10)
for i in Width:
    for j in Depth:
        for l in Depth:
            for n in Priority:
                for t in Time:
                    m.addConstr(x[i,j,i,l,n,t]==0)

#初期値条件
#4-6-23/700
# m.addConstr(b[3,2,0,0] == 1)
# m.addConstr(b[4,1,1,0] == 1)
# m.addConstr(b[2,3,2,0] == 1)
# m.addConstr(b[3,1,3,0] == 1)
# m.addConstr(b[0,0,4,0] == 1)
# m.addConstr(b[3,0,5,0] == 1)
# m.addConstr(b[2,2,6,0] == 1)
# m.addConstr(b[5,3,7,0] == 1)
# m.addConstr(b[0,1,8,0] == 1)
# m.addConstr(b[5,2,9,0] == 1)
# m.addConstr(b[4,0,10,0] == 1)
# m.addConstr(b[0,3,11,0] == 1)
# m.addConstr(b[5,1,12,0] == 1)
# m.addConstr(b[0,2,13,0] == 1)
# m.addConstr(b[2,1,14,0] == 1)
# m.addConstr(b[1,0,15,0] == 1)
# m.addConstr(b[1,1,16,0] == 1)
# m.addConstr(b[1,2,17,0] == 1)
# m.addConstr(b[4,2,18,0] == 1)
# m.addConstr(b[2,0,19,0] == 1)
# m.addConstr(b[3,3,20,0] == 1)
# m.addConstr(b[4,3,21,0] == 1)
# m.addConstr(b[5,0,22,0] == 1)

# m.addConstr(y[3,2,0,0] == 1)

filename = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "/" + "00001" + ".txt"
file = open(filename, "r")
line = file.readline()
for i in Width:
    line = file.readline()
    element = line.split()
    print(element[0])

# #Optimization
# m.optimize()


#Results
# print("Min cost: $",round(m.ObjNVal))

# for f in Factories:
#     if X[f].x > .9:
#         print('-----------'*5)
#         list_customer = []
#         print("Build factory",f)
#         if Z[f].x > .9:
#             print(" and make it big")
#         for c in Customers:
#             if Y[c,f].x >.9:
#                 list_customer.append(c)
#         print('Customers are',list_customer)