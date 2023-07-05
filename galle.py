import gurobipy as gp
from gurobipy import GRB

DEPTH=3
WIDTH=6
NBLOCK=15
N=NBLOCK-WIDTH+1

#Sets
Width = range(WIDTH)
Depth = range(DEPTH)
Nblock= range(NBLOCK+WIDTH)

for row in Width:
    print(row, end=' ')
print()

for row in Depth:
    print(row, end=' ')
print()

for row in Nblock:
    print(row, end=' ')
print()


#Model
m = gp.Model("DBRP")
m.setParam(GRB.Param.LogToConsole, 1)
m.setParam(GRB.Param.OutputFlag, 1)

#Variables
a = { (n,c,d): m.addVar(vtype=GRB.BINARY) for n in range(0,N) for c in range(n-1,NBLOCK+WIDTH) for d in range(n-1,NBLOCK)}
b = { (d): m.addVar(vtype=GRB.BINARY) for d in range(N,NBLOCK)}

#Objective (DBRP)
m.setObjective(gp.quicksum(a[n,n,d] for n in range(0,N-1) for d in range(n,NBLOCK)) +
               gp.quicksum(b[d] for d in range(N,NBLOCK)), GRB.MINIMIZE)


#Constraints
#(2)
for n in range(1,N):
    for c in range(n-1,NBLOCK):
        m.addConstr(gp.quicksum(a[n,NBLOCK+s,c] for s in Width)==1)

#(3)
for n in range(1,N):
    for c in range(n-1,NBLOCK):
        m.addConstr(a[n,c,c] == 0)

#(4)
for n in range(1,N):
    for c in range(n-1,NBLOCK):
        for d in range(n-1,NBLOCK):
            if d == c:
                continue
            m.addConstr(a[n,c,d] + a[n,d,c] <= 1)
                
#(5)
for n in range(1,N):
    for s in Width:
        for c in range(n-1,NBLOCK):
            for d in range(n-1,NBLOCK):
                if d == c:
                    continue
                m.addConstr(a[n,c,d]+a[n,d,c]>=a[n,NBLOCK+s,c]+a[n,NBLOCK+s,d]-1)

#(6)
for n in range(1,N):
    for s in Width:
        for c in range(n-1,NBLOCK):
            for d in range(n-1,NBLOCK):
                if d == c:
                    continue
                m.addConstr(a[n,c,d]+a[n,d,c]<=2-a[n,NBLOCK+s,c]-gp.quicksum(a[n,NBLOCK+r,d] for r in Width if r != s))

#(7)
for n in range(1,N):
    for s in Width:
        m.addConstr(gp.quicksum(a[n,NBLOCK+s,d] for d in range(n-1,NBLOCK)) <= DEPTH)

#(8)
for d in range(N,NBLOCK):
    for c in range(N-1,d-1):
        m.addConstr(b[d]>=a[N-1,c,d])

#(9)
for n in range(0,N-1):
    for c in range(n,NBLOCK):
        for d in range(n,NBLOCK+WIDTH):
            if d == c:
                continue
            m.addConstr(a[n+1,d,c]<=a[n,d,c]+a[n,n,c])

#(10)
for n in range(0,N-1):
    for c in range(n,NBLOCK):
        for d in range(n,NBLOCK+WIDTH):
            if d == c:
                continue
            m.addConstr(a[n+1,d,c]>=a[n,d,c]-a[n,n,c])

#(11)
for n in range(0,N-1):
    for c in range(n,NBLOCK):
        for s in Width:
            m.addConstr(a[n,n,c]+a[n,NBLOCK+s,c]+a[n+1,NBLOCK+s,c]<=2)

#(12)
for n in range(0,N-1):
    for c in range(n,NBLOCK):
        for d in range(n,NBLOCK):
            if d == c:
                continue
            m.addConstr(a[n,n,c]+a[n,n,d]+a[n,c,d]+a[n+1,c,d]<=3)


#初期値条件
#(1))
m.addConstr(a[0,1,6]==1)
m.addConstr(a[0,1,10]==1)
m.addConstr(a[0,2,5]==1)
m.addConstr(a[0,2,9]==1)
m.addConstr(a[0,3,8]==1)
m.addConstr(a[0,3,11]==1)
m.addConstr(a[0,4,7]==1)
m.addConstr(a[0,8,11]==1)
m.addConstr(a[0,9,5]==1)
m.addConstr(a[0,10,6]==1)
m.addConstr(a[0,12,4]==1)
m.addConstr(a[0,12,7]==1)
m.addConstr(a[0,14,13]==1)
m.addConstr(a[0,15,0]==1)
m.addConstr(a[0,16,13]==1)
m.addConstr(a[0,16,14]==1)
m.addConstr(a[0,17,3]==1)
m.addConstr(a[0,17,8]==1)
m.addConstr(a[0,17,11]==1)
m.addConstr(a[0,18,4]==1)
m.addConstr(a[0,18,7]==1)
m.addConstr(a[0,18,12]==1)
m.addConstr(a[0,19,2]==1)
m.addConstr(a[0,19,5]==1)
m.addConstr(a[0,19,9]==1)
m.addConstr(a[0,20,1]==1)
m.addConstr(a[0,20,6]==1)
m.addConstr(a[0,20,10]==1)

# filename = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "/" + "00001" + ".txt"
# file = open(filename, "r")
# line = file.readline()
# for i in Width:
#     line = file.readline()
#     element = line.split()
#     print(element[0])

#Optimization
m.optimize()


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