import gurobipy as gp
from gurobipy import GRB
import time
import csv

DEPTH=3
WIDTH=6
NBLOCK=15
N=NBLOCK-WIDTH+1
NUMBER=1

#計算時間の計測
total_time=0
max_time=0

#最適値
sum_opt=0




for index in range(NUMBER,NUMBER+100*DEPTH):
    start_time=time.time()

    #Model
    m = gp.Model("DBRP")
    # ログ出力を無効化する
    m.setParam('OutputFlag', 0)
    # m.setParam(GRB.Param.LogToConsole, 1)
    # m.setParam(GRB.Param.OutputFlag, 1)

    #Variables
    a = { (n,c,d): m.addVar(vtype=GRB.BINARY) for n in range(0,NBLOCK) for c in range(n,NBLOCK+WIDTH) for d in range(n,NBLOCK)}
    # b = { (d): m.addVar(vtype=GRB.BINARY) for d in range(N,NBLOCK)}
    dir = { (n,bi): m.addVar(vtype=GRB.BINARY) for n in range(0,NBLOCK) for bi in range(0,2)}

    #Objective (DBRP)
    obj1=[]
    obj2=[]
    for n in range(0,NBLOCK):
        obj1.append(gp.quicksum(a[n,n,d] for d in range(n+1,NBLOCK)))
    for n in range(0,NBLOCK):
        obj2.append(gp.quicksum(a[n,d,n] for d in range(n+1,NBLOCK)))

    m.setObjective(gp.quicksum(dir[n,0]*obj1[n] + dir[n,1]*obj2[n] for n in range(0,NBLOCK)), GRB.MINIMIZE)


    #Constraints
    #取り出し方向における制約式
    for n in range(0,NBLOCK):
        m.addConstr(dir[n,0]+dir[n,1]==1)

    #(2)
    for n in range(1,NBLOCK):
        for c in range(n,NBLOCK):
            m.addConstr(gp.quicksum(a[n,NBLOCK+s,c] for s in range(0,WIDTH))==1)

    #(3)
    for n in range(1,NBLOCK):
        for c in range(n,NBLOCK):
            m.addConstr(a[n,c,c] == 0)

    #(4)
    for n in range(1,NBLOCK):
        for c in range(n,NBLOCK):
            for d in range(n,NBLOCK):
                if d == c:
                    continue
                m.addConstr(a[n,c,d] + a[n,d,c] <= 1)
                    
    #(5)
    for n in range(1,NBLOCK):
        for s in range(0,WIDTH):
            for c in range(n,NBLOCK):
                for d in range(n,NBLOCK):
                    if d == c:
                        continue
                    m.addConstr(a[n,c,d]+a[n,d,c]>=a[n,NBLOCK+s,c]+a[n,NBLOCK+s,d]-1)

    #(6)
    for n in range(1,NBLOCK):
        for s in range(0,WIDTH):
            for c in range(n,NBLOCK):
                for d in range(n,NBLOCK):
                    if d == c:
                        continue
                    m.addConstr(a[n,c,d]+a[n,d,c]<=2-a[n,NBLOCK+s,c]-gp.quicksum(a[n,NBLOCK+r,d] for r in range(0,WIDTH) if r != s))

    #(7)
    for n in range(1,NBLOCK):
        for s in range(0,WIDTH):
            m.addConstr(gp.quicksum(a[n,NBLOCK+s,d] for d in range(n,NBLOCK)) <= DEPTH)

    # #(8)
    # for d in range(N,NBLOCK):
    #     for c in range(N-1,d-1):
    #         m.addConstr(b[d]>=a[N-1,c,d])

    #(9)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for d in range(n+1,NBLOCK+WIDTH):
                if d == c:
                    continue
                constr1=a[n+1,d,c]-a[n,d,c]-a[n,n,c]
                constr2=a[n+1,d,c]-a[n,d,c]-a[n,c,n]
                m.addConstr(dir[n,0]*constr1 + dir[n,1]*constr2<=0)


    #(10)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for d in range(n+1,NBLOCK+WIDTH):
                if d == c:
                    continue
                constr1=a[n+1,d,c]-a[n,d,c]+a[n,n,c]
                constr2=a[n+1,d,c]-a[n,d,c]+a[n,c,n]
                m.addConstr(dir[n,0]*constr1 + dir[n,1]*constr2>=0)


    #(11)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for s in range(0,WIDTH):
                constr1=a[n,n,c]+a[n,NBLOCK+s,c]+a[n+1,NBLOCK+s,c]-2
                constr2=a[n,c,n]+a[n,NBLOCK+s,c]+a[n+1,NBLOCK+s,c]-2
                m.addConstr(dir[n,0]*constr1 + dir[n,1]*constr2<=0)

    #(12)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for d in range(n+1,NBLOCK):
                if d == c:
                    continue
                constr1=a[n,n,c]+a[n,n,d]+a[n,c,d]+a[n+1,c,d]-3
                constr2=a[n,c,n]+a[n,d,n]+a[n,c,d]+a[n+1,c,d]-3
                m.addConstr(dir[n,0]*constr1 + dir[n,1]*constr2<=0)


    #初期値条件
    #(1))
    filename = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "/" + str(index).zfill(5) + ".txt"
    print(filename)
    file = open(filename, "r")
    line = file.readline()
    for i in range(0,WIDTH):
        line = file.readline()
        element = line.split()
        for j in range(0,int(element[0])):
            m.addConstr(a[0,i+NBLOCK,int(element[j+1])-1]==1)
            print("{:2}".format(element[j+1])+" ",end=' ')
            for k in range(j,0,-1):
                m.addConstr(a[0,int(element[k])-1,int(element[j+1])-1]==1)
        print()
    file.close()


    #Optimization
    m.optimize()

    end_time=time.time()
    elapsed_time=end_time-start_time
    total_time+=elapsed_time
    if(max_time<elapsed_time):
        max_time=elapsed_time

    sum_opt+=m.ObjVal

    #Results
    print("optimal value:",round(m.ObjVal))

    # for c in range(10,NBLOCK):
    #     for d in range(10,NBLOCK):
    #         print(a[10,c,d].x,end=' ')
    #     print()

    # input()

    if index%100 == 1:
        #ファイルに結果を書き込む
        filename = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "(ip)"+".csv"
        w_file=open(filename,"w")
    w_file.write(str(round(m.objVal)))
    w_file.write("\n")

    if index%100 == 0:
        NBLOCK+=1
        w_file.close()

print("optimal_value:",sum_opt/(100*DEPTH),"average time:",total_time/(100*DEPTH),"max time:",max_time)

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