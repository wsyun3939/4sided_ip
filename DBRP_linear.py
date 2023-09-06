import gurobipy as gp
from gurobipy import GRB
import time
import csv

DEPTH=3
WIDTH=8
NBLOCK=21
N=NBLOCK-WIDTH+1
NUMBER=5001

#計算時間の計測
total_time=0
max_time=0

# 最適値
opt=0

#最適値の合計
sum_opt=0

# 30分以内に解けなかったインスタンスの数
timeup=0




for index in range(NUMBER,NUMBER+100*DEPTH):

    #Model
    m = gp.Model("DBRP")
    # ログ出力を無効化する
    m.setParam('OutputFlag', 0)
    # ３０分の制限時間を設ける
    m.setParam("TimeLimit", 1800)
    # m.setParam(GRB.Param.LogToConsole, 1)
    # m.setParam(GRB.Param.OutputFlag, 1)

    #Variables
    a = { (n,c,d): m.addVar(vtype=GRB.BINARY) for n in range(0,NBLOCK) for c in range(n,NBLOCK+WIDTH) for d in range(n,NBLOCK)}
    x = { (n,dir,d): m.addVar(vtype=GRB.BINARY) for n in range(0,NBLOCK) for dir in range(0,2) for d in range(n+1,NBLOCK)}
    dir = { (n): m.addVar(vtype=GRB.BINARY) for n in range(0,NBLOCK)}

    #Objective (DBRP)
    obj1=[]
    obj2=[]
    for n in range(0,NBLOCK):
        obj1.append(gp.quicksum(x[n,0,d] for d in range(n+1,NBLOCK)))
    for n in range(0,NBLOCK):
        obj2.append(gp.quicksum(x[n,1,d] for d in range(n+1,NBLOCK)))

    m.setObjective(gp.quicksum(obj1[n]+obj2[n] for n in range(0,NBLOCK)), GRB.MINIMIZE)


    #Constraints

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

    #(9)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for d in range(n+1,NBLOCK+WIDTH):
                if d == c:
                    continue
                m.addConstr(a[n+1,d,c]-a[n,d,c]-a[n,n,c]<=dir[n])
                m.addConstr(a[n+1,d,c]-a[n,d,c]-a[n,c,n]<=1-dir[n])


    #(10)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for d in range(n+1,NBLOCK+WIDTH):
                if d == c:
                    continue
                m.addConstr(a[n+1,d,c]-a[n,d,c]+a[n,n,c]>=-1*dir[n])
                m.addConstr(a[n+1,d,c]-a[n,d,c]+a[n,c,n]>=-1*(1-dir[n]))


    #(11)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for s in range(0,WIDTH):
                m.addConstr(a[n,n,c]+a[n,NBLOCK+s,c]+a[n+1,NBLOCK+s,c]-2<=dir[n])
                m.addConstr(a[n,c,n]+a[n,NBLOCK+s,c]+a[n+1,NBLOCK+s,c]-2<=1-dir[n])

    #(12)
    for n in range(0,NBLOCK):
        for c in range(n+1,NBLOCK):
            for d in range(n+1,NBLOCK):
                if d == c:
                    continue
                m.addConstr(a[n,n,c]+a[n,n,d]+a[n,c,d]+a[n+1,c,d]-3<=dir[n])
                m.addConstr(a[n,c,n]+a[n,d,n]+a[n,c,d]+a[n+1,c,d]-3<=1-dir[n])

    for n in range(0,NBLOCK):
        for d in range(n+1,NBLOCK):
            m.addConstr((1-dir[n])+a[n,n,d]-1<=x[n,0,d])
            m.addConstr((1-dir[n])>=x[n,0,d])
            m.addConstr(a[n,n,d]>=x[n,0,d])
            m.addConstr(dir[n]+a[n,d,n]-1<=x[n,1,d])
            m.addConstr(dir[n]>=x[n,1,d])
            m.addConstr(a[n,d,n]>=x[n,1,d])


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


    start_time=time.time()

    #Optimization
    m.optimize()

    if(m.status == GRB.TIME_LIMIT):
        print("time limit")
        timeup+=1
        opt=-1
    else:
        end_time=time.time()
        elapsed_time=end_time-start_time
        total_time+=elapsed_time
        if(max_time<elapsed_time):
            max_time=elapsed_time

        opt=round(m.ObjVal)
        sum_opt+=opt

    #Results
    print("optimal value:",opt)

    if index%100 == 1:
        #ファイルに結果を書き込む
        filename = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "(ip2d)"+".csv"
        w_file=open(filename,"w")
    w_file.write(str(opt))
    w_file.write("\n")

    if index%100 == 0:
        NBLOCK+=1
        w_file.close()

print("optimal_value:",sum_opt/(100*DEPTH-timeup),"average time:",total_time/(100*DEPTH-timeup),"max time:",max_time,"timeup:",timeup)

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