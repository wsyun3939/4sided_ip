import gurobipy as gp
from gurobipy import GRB
import time

DEPTH=3
WIDTH=6
NBLOCK=16
NUMBER=109

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
    x = { (i,j,k,l,n,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) for n in range(t+1,NBLOCK)}
    y = { (i,j,t,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for t in range(0,NBLOCK-1)}
    b = { (i,j,n,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for t in range(0,NBLOCK) for n in range(t,NBLOCK) }
    #取り出し方向を表す変数(0の時は上，1の時は右)
    dir = { (n): m.addVar(vtype=GRB.BINARY) for n in range(0,NBLOCK)}
    #上右下左にブロックがあるかどうか判断する変数
    upp = { (i,j,k,l,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) }
    right = { (i,j,k,l,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) }
    down = { (k,l,t): m.addVar(vtype=GRB.BINARY) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) }
    left = { (k,l,t): m.addVar(vtype=GRB.BINARY) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) }
    #積み替えが成立するかどうか判断する変数
    rel_down = { (i,j,k,l,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) }
    rel_left = { (i,j,k,l,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) }

    #Objective (DBRP)
    m.setObjective(gp.quicksum(x[i,j,k,l,n,t] for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,WIDTH) for l in range(0,DEPTH) for t in range(0,NBLOCK-1) for n in range(t+1,NBLOCK) ), GRB.MINIMIZE)



    #Constraints

    # for n in range(0,NBLOCK):
    #     m.addConstr(dir[n]==0)

    # m.addConstr(dir[0]==1)

    #(2)ブロックは各スロットに１つのみ
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr(gp.quicksum(b[i,j,n,t] for n in range(t,NBLOCK)) <= 1)

    #(6a)ブロック配置は積み替えによって遷移する
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                for n in range(t+1,NBLOCK):   
                    m.addConstr(b[i,j,n,t+1]==b[i,j,n,t]+gp.quicksum(x[k,l,i,j,n,t] for k in range(0,WIDTH) for l in range(0,DEPTH)) - 
                                    gp.quicksum(x[i,j,k,l,n,t] for k in range(0,WIDTH) for l in range(0,DEPTH)))
                    
    # (6b)各時間において，ひとつだけブロックが取り出される
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr(b[i,j,t,t]-y[i,j,t,t]==0)

    #(7'')ターゲットブロックは一つ
    for t in range(0,NBLOCK-1):
        m.addConstr(gp.quicksum(y[i,j,t,t] for i in range(0,WIDTH) for j in range(0,DEPTH)) == 1)

    #(8')各取り出し方向において，LIFOが成り立つようににする
    for k in range(0,WIDTH):
        for t in range(0,NBLOCK-1):
            for l in range(0,DEPTH):
                b_sum_1 = gp.quicksum(b[k,l_dash,n,t] for n in range(t+1,NBLOCK) for l_dash in range(l-1,-1,-1))
                m.addConstr(b_sum_1<=DEPTH*down[k,l,t])
                m.addConstr(down[k,l,t]<=b_sum_1)
                b_sum_2 = gp.quicksum(b[k_dash,l,n,t] for n in range(t+1,NBLOCK) for k_dash in range(k-1,-1,-1))
                m.addConstr(b_sum_2<=WIDTH*left[k,l,t])
                m.addConstr(left[k,l,t]<=b_sum_2)
                for i in range(0,WIDTH):
                    for j in range(0,DEPTH):
                        x_sum = gp.quicksum(x[i,j,k,l,n,t] for n in range(t+1,NBLOCK))
                        x_sum_1 = gp.quicksum(x[i,j_dash,k,l_dash,n,t] for n in range(t+1,NBLOCK) for j_dash in range(j+1,DEPTH) for l_dash in range(l+1,DEPTH))
                        x_sum_2 = gp.quicksum(x[i,j_dash,k_dash,l,n,t] for n in range(t+1,NBLOCK) for j_dash in range(j+1,DEPTH) for k_dash in range(k+1,WIDTH))

                        m.addConstr((1-x_sum_1)+3>=(1-dir[t])+x_sum+down[k,l,t]+(1-left[k,l,t]))
                        m.addConstr((1-x_sum_2)+3>=(1-dir[t])+x_sum+left[k,l,t]+(1-down[k,l,t]))
    for i in range(0,WIDTH):
        for k in range(0,WIDTH):
            for j in range(0,DEPTH):
                for l in range(0,DEPTH):
                    for t in range(0,NBLOCK-1):
                        x_sum = gp.quicksum(x[i,j,k,l,n,t] for n in range(t+1,NBLOCK))
                        x_sum_1 = gp.quicksum(x[i_dash,j,k,l_dash,n,t] for n in range(t+1,NBLOCK) for i_dash in range(i+1,WIDTH) for l_dash in range(l+1,DEPTH))
                        x_sum_2 = gp.quicksum(x[i_dash,j,k_dash,l,n,t] for n in range(t+1,NBLOCK) for i_dash in range(i+1,WIDTH) for k_dash in range(k+1,WIDTH))

                        m.addConstr((1-x_sum_1)+3>=dir[t]+x_sum+down[k,l,t]+(1-left[k,l,t]))
                        m.addConstr((1-x_sum_2)+3>=dir[t]+x_sum+left[k,l,t]+(1-down[k,l,t]))


    #(10)ターゲットブロックの空きスペースへの移動は禁止
    for k in range(0,WIDTH):
        for l in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr((1-dir[t])+gp.quicksum(y[k,l_dash,t,t] for l_dash in range(0,l+1))-1<=1-gp.quicksum(x[k,j,k,l,n,t] for j in range(0,DEPTH) for n in range(t+1,NBLOCK)))
                m.addConstr(dir[t]+gp.quicksum(y[k,l_dash,t,t] for l_dash in range(l,DEPTH))-1<=1-gp.quicksum(x[k,j,k,l,n,t] for j in range(0,DEPTH) for n in range(t+1,NBLOCK)))

    #(A')取り出し方向に位置するブロッキングブロックは必ず積み替える
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr((1-dir[t]) + (1-gp.quicksum(y[i,j_dash,t,t] for j_dash in range(0,j))) - 1 <= 1 - gp.quicksum(x[i,j,k,l,n,t] for k in range(0,WIDTH) for l in range(0,DEPTH) for n in range(t+1,NBLOCK)))
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr((1-dir[t]) + gp.quicksum(b[i,j,n,t] for n in range(t+1,NBLOCK)) - 1 <= 1-(gp.quicksum(y[i,j_dash,t,t] for j_dash in range(0,j))-gp.quicksum(x[i,j,k,l,n,t] for k in range(0,WIDTH) for l in range(0,DEPTH) for n in range(t+1,NBLOCK))))

    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr(dir[t] + (1-gp.quicksum(y[i_dash,j,t,t] for i_dash in range(0,i))) - 1 <= 1 - gp.quicksum(x[i,j,k,l,n,t] for k in range(0,WIDTH) for l in range(0,DEPTH) for n in range(t+1,NBLOCK)))
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr(dir[t] + gp.quicksum(b[i,j,n,t] for n in range(t+1,NBLOCK)) - 1 <= 1 - (gp.quicksum(y[i_dash,j,t,t] for i_dash in range(0,i))-gp.quicksum(x[i,j,k,l,n,t] for k in range(0,WIDTH) for l in range(0,DEPTH) for n in range(t+1,NBLOCK))))

    #自己位置への積み替えは禁止
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for t in range(0,NBLOCK-1):
                m.addConstr(gp.quicksum(x[i,j,i,j,n,t] for n in range(t+1,NBLOCK)) == 0)

    #デックが空の場合，両端へと積み替える
    for i in range(0,WIDTH):
        for t in range(0,NBLOCK-1):
            m.addConstr(dir[t]>=gp.quicksum(x[i,j,i,l,n,t] for j in range(0,DEPTH) for l in range(0,DEPTH) for n in range(t+1,NBLOCK)))
    for j in range(0,DEPTH):
        for t in range(0,NBLOCK-1):
            m.addConstr(dir[t]<=1-gp.quicksum(x[i,j,k,j,n,t] for i in range(0,WIDTH) for k in range(0,WIDTH) for n in range(t+1,NBLOCK)))

    #積み替えは押し込むようにする
    for i in range(0,WIDTH):
        for j in range(0,DEPTH):
            for k in range(0,WIDTH):
                for t in range(0,NBLOCK-1):
                    for l in range(0,DEPTH):
                        b_low=1
                        b_left=1
                        if l > 0:
                            b_low=gp.quicksum(b[k,l-1,n,t] for n in range(t+1,NBLOCK))+gp.quicksum(x[i,j_dash,k,l-1,n,t] for j_dash in range(j+1,DEPTH) for n in range(t+1,NBLOCK))+gp.quicksum(x[i_dash,j,k,l-1,n,t] for i_dash in range(i+1,WIDTH) for n in range(t+1,NBLOCK))
                        if k > 0:
                            b_left=gp.quicksum(b[k-1,l,n,t] for n in range(t+1,NBLOCK))+gp.quicksum(x[i,j_dash,k-1,l,n,t] for j_dash in range(j+1,DEPTH) for n in range(t+1,NBLOCK))+gp.quicksum(x[i_dash,j,k-1,l,n,t] for i_dash in range(i+1,WIDTH) for n in range(t+1,NBLOCK))
                        if k-1==i and l>j:
                            b_left-=gp.quicksum(x[k-1,l,width,depth,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for n in range(t+1,NBLOCK))
                        if k>=i and l-1==j:
                            b_low-=gp.quicksum(x[k,l-1,width,depth,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for n in range(t+1,NBLOCK))
                        upper_sum=gp.quicksum(b[k,l_dash,n,t] for n in range(t+1,NBLOCK) for l_dash in range(l+1,DEPTH))
                        righter_sum=gp.quicksum(b[k_dash,l,n,t] for n in range(t+1,NBLOCK) for k_dash in range(k+1,WIDTH))
                        if k>i:
                            upper_sum-=gp.quicksum(x[k,l_dash,width,depth,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for n in range(t+1,NBLOCK) for l_dash in range(l+1,DEPTH))
                        if l>j:
                            righter_sum-=gp.quicksum(x[k_dash,l,width,depth,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for n in range(t+1,NBLOCK) for k_dash in range(k+1,WIDTH))
                        m.addConstr(upper_sum<=DEPTH*upp[i,j,k,l,t])
                        m.addConstr(upp[i,j,k,l,t]<=upper_sum)
                        m.addConstr(righter_sum<=WIDTH*right[i,j,k,l,t])
                        m.addConstr(right[i,j,k,l,t]<=righter_sum)
                        m.addConstr(rel_down[i,j,k,l,t]>=b_low+(1-upp[i,j,k,l,t])-1)
                        m.addConstr(rel_down[i,j,k,l,t]<=b_low)
                        m.addConstr(rel_down[i,j,k,l,t]<=1-upp[i,j,k,l,t])
                        m.addConstr(rel_left[i,j,k,l,t]>=b_left+(1-right[i,j,k,l,t])-1)
                        m.addConstr(rel_left[i,j,k,l,t]<=b_left)
                        m.addConstr(rel_left[i,j,k,l,t]<=1-right[i,j,k,l,t])
                        m.addConstr(rel_down[i,j,k,l,t]+rel_left[i,j,k,l,t]>=gp.quicksum(x[i,j,k,l,n,t] for n in range(t+1,NBLOCK)))

    # for i in range(0,WIDTH):
    #     for j in range(0,DEPTH):
    #             m.addConstr(b[i,j,2,0]==0)
    # m.addConstr(b[0,1,0,0] == 1)
    # m.addConstr(b[0,0,1,0] == 1)

    # m.addConstr(y[0,1,0,0] == 1)

    #初期値条件
    #3-6-15/1
    # m.addConstr(b[0,0,0,0] == 1)
    # m.addConstr(b[5,0,1,0] == 1)
    # m.addConstr(b[4,0,2,0] == 1)
    # m.addConstr(b[2,0,3,0] == 1)
    # m.addConstr(b[3,1,4,0] == 1)
    # m.addConstr(b[4,2,5,0] == 1)
    # m.addConstr(b[5,2,6,0] == 1)
    # m.addConstr(b[3,2,7,0] == 1)
    # m.addConstr(b[2,1,8,0] == 1)
    # m.addConstr(b[4,1,9,0] == 1)
    # m.addConstr(b[5,1,10,0] == 1)
    # m.addConstr(b[2,2,11,0] == 1)
    # m.addConstr(b[3,0,12,0] == 1)
    # m.addConstr(b[1,1,13,0] == 1)
    # m.addConstr(b[1,0,14,0] == 1)

    # m.addConstr(y[0,0,0,0] == 1)

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

    #初期値条件
    #(1)
    filename = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "/" + str(index).zfill(5) + ".txt"
    print(filename)
    file = open(filename, "r")
    line = file.readline()
    for i in range(0,WIDTH):
        line = file.readline()
        element = line.split()
        for j in range(0,int(element[0])):
            m.addConstr(b[i,j,int(element[j+1])-1,0]==1)
            print("{:2}".format(element[j+1])+" ",end=' ')
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

    break

    if index%100 == 1:
        #ファイルに結果を書き込む
        filename = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "(ip2)"+".csv"
        w_file=open(filename,"w")
    w_file.write(str(opt))
    w_file.write("\n")

    if index%100 == 0:
        NBLOCK+=1
        w_file.close()


print("optimal_value:",sum_opt/(100*DEPTH-timeup),"average time:",total_time/(100*DEPTH-timeup),"max time:",max_time)

#決定変数の値を表示
for t in range(0,NBLOCK):
    print("t=",t+1)
    print("dir=",dir[t].x)
    block=[[0 for j in range(DEPTH)] for i in range(WIDTH)]
    for n in range(t,NBLOCK):
        for i in range(0,WIDTH):
            for j in range(0,DEPTH):
                if b[i,j,n,t].x==1:
                    block[i][j]=n+1
    for j in range(DEPTH-1,-1,-1):
        for i in range(0,WIDTH):
            print("{:2}".format(block[i][j]),end=" ")
        print("")
    for n in range(t+1,NBLOCK):
        for i in range(0,WIDTH):
            for j in range(0,DEPTH):
                for k in range(0,WIDTH):
                    for l in range(0,DEPTH):
                        if x[i,j,k,l,n,t].x==1:
                            print("(",i,j,")","(",k,l,")",n+1)
                            total_sum=0
                            if l>0:
                                for n in range(t+1,NBLOCK):
                                    total_sum+=b[k,l-1,n,t].x
                                    for j_dash in range(j+1,DEPTH):
                                        total_sum+=x[i,j_dash,k,l-1,n,t].x
                                print("b_low=",total_sum)
                            print("rel_down=",rel_down[i,j,k,l,t].x)
                            print("rel_left=",rel_left[i,j,k,l,t].x)
