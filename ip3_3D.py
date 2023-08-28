import gurobipy as gp
from gurobipy import GRB
import time

DEPTH=3
WIDTH=4
HEIGHT=2
NBLOCK=12
NUMBER=1

#計算時間の計測
total_time=0
max_time=0

# 最適値
opt=0

#最適値の合計
sum_opt=0

# 30分以内に解けなかったインスタンスの数
timeup=0




for itr in range(0,DEPTH):
    for index in range(NUMBER,NUMBER+100):

        #Model
        m = gp.Model("DBRP")
        # ログ出力を無効化する
        m.setParam('OutputFlag', 0)
        # ３０分の制限時間を設ける
        m.setParam("TimeLimit", 1800)
        # m.setParam(GRB.Param.LogToConsole, 1)
        # m.setParam(GRB.Param.OutputFlag, 1)

        #Variables
        x = { (i1,j1,k1,i2,j2,k2,n,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) for n in range(t+1,NBLOCK)}
        y = { (i,j,k,t,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,HEIGHT) for t in range(0,NBLOCK-1)}
        b = { (i,j,k,n,t): m.addVar(vtype=GRB.BINARY) for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(0,HEIGHT) for t in range(0,NBLOCK) for n in range(t,NBLOCK) }
        #取り出し方向を表す変数(0の時は上，1の時は右) u(上)=0,l(右)=1,d(下)=2
        dir = { (n,urd): m.addVar(vtype=GRB.BINARY) for n in range(0,NBLOCK) for urd in range(0,3)}
        #上右下左にブロックがあるかどうか判断する変数
        upp = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        right = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        down = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        front = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        rightback = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        rear = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        #積み替えが成立するかどうか判断する変数
        rel_upp = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        rel_upp1 = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        rel_right = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        rel_right1 = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        rel_down = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }
        rel_down1 = { (i1,j1,k1,i2,j2,k2,t): m.addVar(vtype=GRB.BINARY) for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) }

        #Objective (DBRP)
        m.setObjective(gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for t in range(0,NBLOCK-1) for n in range(t+1,NBLOCK) ), GRB.MINIMIZE)



        #Constraints

        # for n in range(0,NBLOCK):
        #     m.addConstr(dir[n]==0)

        # m.addConstr(dir[0]==0)

        # m.addConstr(b[2,1,15,0]==0)

        # m.addConstr(x[3,0,1,1,2,1,11,3]==0)
        # m.addConstr(x[3,0,1,1,1,1,11,3]==0)
        # m.addConstr(x[3,0,1,1,2,0,11,3]==0)
        # m.addConstr(x[3,0,1,1,0,0,11,3]==1)
        # m.addConstr(gp.quicksum(x[3,0,1,i,j,k,11,3] for i in range(0,WIDTH) for j in range(0,DEPTH) for k in range(1,HEIGHT))==0)

        #各時間において取り出し方向を決定する
        for t in range(0,NBLOCK-1):
            m.addConstr(gp.quicksum(dir[t,urd] for urd in range(0,3))==1)

        #(2)ブロックは各スロットに１つのみ
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(gp.quicksum(b[i1,j1,k1,n,t] for n in range(t,NBLOCK)) <= 1)

        #(6a)ブロック配置は積み替えによって遷移する
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        for n in range(t+1,NBLOCK):   
                            m.addConstr(b[i1,j1,k1,n,t+1]==b[i1,j1,k1,n,t]+gp.quicksum(x[i2,j2,k2,i1,j1,k1,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT))-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT)))
                        
        # (6b)各時間において，ひとつだけブロックが取り出される
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(b[i1,j1,k1,t,t]-y[i1,j1,k1,t,t]==0)

        #(7'')ターゲットブロックは一つ
        for t in range(0,NBLOCK-1):
            m.addConstr(gp.quicksum(y[i1,j1,k1,t,t] for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT)) == 1)

        
        #(10)ブロッキングブロックとなるような積み替えは禁止
        for i2 in range(0,WIDTH):
            for j2 in range(0,DEPTH):
                for k2 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(dir[t,0]+gp.quicksum(y[i2,j_dash,k_dash,t,t] for j_dash in range(0,j2) for k_dash in range(0,HEIGHT))+gp.quicksum(y[i2,j2,k_dash,t,t] for k_dash in range(0,k2+1))-1<=1-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for n in range(t+1,NBLOCK)))
                        m.addConstr(dir[t,1]+gp.quicksum(y[i_dash,j2,k_dash,t,t] for i_dash in range(0,i2) for k_dash in range(0,HEIGHT))+gp.quicksum(y[i2,j2,k_dash,t,t] for k_dash in range(0,k2+1))-1<=1-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for n in range(t+1,NBLOCK)))
                        m.addConstr(dir[t,2]+gp.quicksum(y[i2,j_dash,k_dash,t,t] for j_dash in range(j2+1,DEPTH) for k_dash in range(0,HEIGHT))+gp.quicksum(y[i2,j2,k_dash,t,t] for k_dash in range(0,k2+1))-1<=1-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i1 in range(0,WIDTH) for j1 in range(0,DEPTH) for k1 in range(0,HEIGHT) for n in range(t+1,NBLOCK)))

        #(A')取り出し方向に位置するブロッキングブロックは必ず積み替える
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(dir[t,0]-gp.quicksum(y[i1,j_dash,k_dash,t,t] for j_dash in range(0,j1) for k_dash in range(0,HEIGHT))-gp.quicksum(y[i1,j1,k_dash,t,t] for k_dash in range(0,k1)) <= 1-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for n in range(t+1,NBLOCK)))
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(dir[t,0]+gp.quicksum(b[i1,j1,k1,n,t] for n in range(t+1,NBLOCK))-1 <= 1-(gp.quicksum(y[i1,j_dash,k_dash,t,t] for j_dash in range(0,j1) for k_dash in range(0,HEIGHT))+gp.quicksum(y[i1,j1,k_dash,t,t] for k_dash in range(0,k1))-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))))

        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(dir[t,1]-gp.quicksum(y[i_dash,j1,k_dash,t,t] for i_dash in range(0,i1) for k_dash in range(0,HEIGHT))-gp.quicksum(y[i1,j1,k_dash,t,t] for k_dash in range(0,k1)) <= 1-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for n in range(t+1,NBLOCK)))
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(dir[t,1]+gp.quicksum(b[i1,j1,k1,n,t] for n in range(t+1,NBLOCK))-1 <= 1-(gp.quicksum(y[i_dash,j1,k_dash,t,t] for i_dash in range(0,i1) for k_dash in range(0,HEIGHT))+gp.quicksum(y[i1,j1,k_dash,t,t] for k_dash in range(0,k1))-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))))

        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(dir[t,2]-gp.quicksum(y[i1,j_dash,k_dash,t,t] for j_dash in range(j1+1,DEPTH) for k_dash in range(0,HEIGHT))-gp.quicksum(y[i1,j1,k_dash,t,t] for k_dash in range(0,k1)) <= 1-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for n in range(t+1,NBLOCK)))
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for t in range(0,NBLOCK-1):
                        m.addConstr(dir[t,2]+gp.quicksum(b[i1,j1,k1,n,t] for n in range(t+1,NBLOCK))-1 <= 1-(gp.quicksum(y[i1,j_dash,k_dash,t,t] for j_dash in range(j1+1,DEPTH) for k_dash in range(0,HEIGHT))+gp.quicksum(y[i1,j1,k_dash,t,t] for k_dash in range(0,k1))-gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for i2 in range(0,WIDTH) for j2 in range(0,DEPTH) for k2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))))


        #積み替えは押し込むようにする
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for i2 in range(0,WIDTH):
                        for j2 in range(0,DEPTH):
                            for k2 in range(0,HEIGHT):
                                for t in range(0,NBLOCK-1):
                                    x_sum=gp.quicksum(x[i1,j1,k1,i2,j2,k2,n,t] for n in range(t+1,NBLOCK))
                                    #高さ０における積み替え
                                    if k2==0:
                                        b_low=1
                                        b_left=1
                                        b_high=1
                                        if j2 > 0:
                                            b_low=gp.quicksum(b[i2,j2-1,k2,n,t] for n in range(t+1,NBLOCK))+dir[t,0]*gp.quicksum(x[i1,j_dash,k_dash,i2,j2-1,k2,n,t] for j_dash in range(j1+1,DEPTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,2]*gp.quicksum(x[i1,j_dash,k_dash,i2,j2-1,k2,n,t] for j_dash in range(0,j1) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+gp.quicksum(x[i1,j1,k_dash,i2,j2-1,k2,n,t] for k_dash in range(k1+1,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,1]*gp.quicksum(x[i_dash,j1,k_dash,i2,j2-1,k2,n,t] for i_dash in range(i1+1,WIDTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2 > 0:
                                            b_left=gp.quicksum(b[i2-1,j2,k2,n,t] for n in range(t+1,NBLOCK))+dir[t,1]*gp.quicksum(x[i_dash,j1,k_dash,i2-1,j2,k2,n,t] for i_dash in range(i1+1,WIDTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+gp.quicksum(x[i1,j1,k_dash,i2-1,j2,k2,n,t] for k_dash in range(k1+1,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,0]*gp.quicksum(x[i1,j_dash,k_dash,i2-1,j2,k2,n,t] for j_dash in range(j1+1,DEPTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,2]*gp.quicksum(x[i1,j_dash,k_dash,i2-1,j2,k2,n,t] for j_dash in range(0,j1) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if j2 < DEPTH-1:
                                            b_high=gp.quicksum(b[i2,j2+1,k2,n,t] for n in range(t+1,NBLOCK))+dir[t,0]*gp.quicksum(x[i1,j_dash,k_dash,i2,j2+1,k2,n,t] for j_dash in range(j1+1,DEPTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,2]*gp.quicksum(x[i1,j_dash,k_dash,i2,j2+1,k2,n,t] for j_dash in range(0,j1) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+gp.quicksum(x[i1,j1,k_dash,i2,j2+1,k2,n,t] for k_dash in range(k1+1,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,1]*gp.quicksum(x[i_dash,j1,k_dash,i2,j2+1,k2,n,t] for i_dash in range(i1+1,WIDTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2-1==i1 and j2>j1:
                                            b_left-=dir[t,0]*gp.quicksum(x[i2-1,j2,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2-1==i1 and j2==j1 and k2>=k1:
                                            b_left-=dir[t,0]*gp.quicksum(x[i2-1,j2,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2>i1 and j2-1==j1:
                                            b_low-=dir[t,1]*gp.quicksum(x[i2,j2-1,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2==i1 and j2-1==j1 and k2>=k1:
                                            b_low-=dir[t,1]*gp.quicksum(x[i2,j2-1,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2>i1 and j2+1==j1:
                                            b_high-=dir[t,1]*gp.quicksum(x[i2,j2+1,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2==i1 and j2+1==j1 and k2>=k1:
                                            b_high-=dir[t,1]*gp.quicksum(x[i2,j2+1,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2-1==i1 and j2<j1:
                                            b_left-=dir[t,2]*gp.quicksum(x[i2-1,j2,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2-1==i1 and j2==j1 and k2>=k1:
                                            b_left-=dir[t,2]*gp.quicksum(x[i2-1,j2,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        upper_sum=gp.quicksum(b[i2,j_dash,k2,n,t] for n in range(t+1,NBLOCK) for j_dash in range(j2+1,DEPTH))
                                        righter_sum=gp.quicksum(b[i_dash,j2,k2,n,t] for n in range(t+1,NBLOCK) for i_dash in range(i2+1,WIDTH))
                                        downer_sum=gp.quicksum(b[i2,j_dash,k2,n,t] for n in range(t+1,NBLOCK) for j_dash in range(0,j2))
                                        if i2>=i1:
                                            upper_sum-=dir[t,1]*gp.quicksum(x[i2,j_dash,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for j_dash in range(j2+1,DEPTH))
                                            downer_sum-=dir[t,1]*gp.quicksum(x[i2,j_dash,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for j_dash in range(0,j2))
                                        if j2>=j1:
                                            righter_sum-=dir[t,0]*gp.quicksum(x[i_dash,j2,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for i_dash in range(i2+1,WIDTH))
                                        if j2<=j1:
                                            righter_sum-=dir[t,2]*gp.quicksum(x[i_dash,j2,k2,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for i_dash in range(i2+1,WIDTH))
                                        m.addConstr(upper_sum<=DEPTH*upp[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(upp[i1,j1,k1,i2,j2,k2,t]<=upper_sum)
                                        m.addConstr(righter_sum<=WIDTH*right[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(right[i1,j1,k1,i2,j2,k2,t]<=righter_sum)
                                        m.addConstr(downer_sum<=DEPTH*down[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(down[i1,j1,k1,i2,j2,k2,t]<=downer_sum)
                                        m.addConstr(rel_upp[i1,j1,k1,i2,j2,k2,t]>=b_low+(1-upp[i1,j1,k1,i2,j2,k2,t])-1)
                                        m.addConstr(rel_upp[i1,j1,k1,i2,j2,k2,t]<=b_low)
                                        m.addConstr(rel_upp[i1,j1,k1,i2,j2,k2,t]<=1-upp[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(rel_right[i1,j1,k1,i2,j2,k2,t]>=b_left+(1-right[i1,j1,k1,i2,j2,k2,t])-1)
                                        m.addConstr(rel_right[i1,j1,k1,i2,j2,k2,t]<=b_left)
                                        m.addConstr(rel_right[i1,j1,k1,i2,j2,k2,t]<=1-right[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(rel_down[i1,j1,k1,i2,j2,k2,t]>=b_high+(1-down[i1,j1,k1,i2,j2,k2,t])-1)
                                        m.addConstr(rel_down[i1,j1,k1,i2,j2,k2,t]<=b_high)
                                        m.addConstr(rel_down[i1,j1,k1,i2,j2,k2,t]<=1-down[i1,j1,k1,i2,j2,k2,t])

                                        m.addConstr(rel_upp1[i1,j1,k1,i2,j2,k2,t]==0)
                                        m.addConstr(rel_right1[i1,j1,k1,i2,j2,k2,t]==0)
                                        m.addConstr(rel_down1[i1,j1,k1,i2,j2,k2,t]==0)
                                        m.addConstr(gp.quicksum(rel_upp[i1,j1,k1,i2,j2,k_dash2,t] for k_dash2 in range(1,HEIGHT))==0)
                                        m.addConstr(gp.quicksum(rel_right[i1,j1,k1,i2,j2,k_dash2,t] for k_dash2 in range(1,HEIGHT))==0)
                                        m.addConstr(gp.quicksum(rel_down[i1,j1,k1,i2,j2,k_dash2,t] for k_dash2 in range(1,HEIGHT))==0)
                                    

                                    # 高さ０以外での積み替え
                                    if k2>0:
                                        b_below=gp.quicksum(b[i2,j2,k2-1,n,t] for n in range(t+1,NBLOCK))+dir[t,0]*gp.quicksum(x[i1,j_dash,k_dash,i2,j2,k2-1,n,t] for j_dash in range(j1+1,DEPTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,2]*gp.quicksum(x[i1,j_dash,k_dash,i2,j2,k2-1,n,t] for j_dash in range(0,j1) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))+gp.quicksum(x[i1,j1,k_dash,i2,j2,k2-1,n,t] for k_dash in range(k1+1,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,1]*gp.quicksum(x[i_dash,j1,k_dash,i2,j2,k2-1,n,t] for i_dash in range(i1+1,WIDTH) for k_dash in range(0,HEIGHT) for n in range(t+1,NBLOCK))

                                        front_sum=gp.quicksum(b[i2,j_dash,k_dash,n,t] for n in range(t+1,NBLOCK) for j_dash in range(j2+1,DEPTH) for k_dash in range(0,HEIGHT))+dir[t,0]*gp.quicksum(x[i1,j_dash1,k_dash1,i2,j_dash2,k_dash2,n,t] for j_dash1 in range(j1+1,DEPTH) for k_dash1 in range(0,HEIGHT) for j_dash2 in range(j2+1,DEPTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+gp.quicksum(x[i1,j1,k_dash1,i2,j_dash2,k_dash2,n,t] for k_dash1 in range(k1+1,HEIGHT) for j_dash2 in range(j2+1,DEPTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,2]*gp.quicksum(x[i1,j_dash1,k_dash1,i2,j_dash2,k_dash2,n,t] for j_dash1 in range(0,j1) for k_dash1 in range(0,HEIGHT) for j_dash2 in range(j2+1,DEPTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,1]*gp.quicksum(x[i_dash1,j1,k_dash1,i2,j_dash2,k_dash2,n,t] for i_dash1 in range(i1+1,WIDTH) for k_dash1 in range(0,HEIGHT) for j_dash2 in range(j2+1,DEPTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2>=i1:
                                            front_sum-=dir[t,1]*gp.quicksum(x[i2,j_dash,k_dash,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for j_dash in range(j2+1,DEPTH) for k_dash in range(0,HEIGHT))
                                        
                                        rightback_sum=gp.quicksum(b[i_dash,j2,k_dash,n,t] for n in range(t+1,NBLOCK) for i_dash in range(i2+1,WIDTH) for k_dash in range(0,HEIGHT))+dir[t,0]*gp.quicksum(x[i1,j_dash1,k_dash1,i_dash2,j2,k_dash2,n,t] for j_dash1 in range(j1+1,DEPTH) for k_dash1 in range(0,HEIGHT) for i_dash2 in range(i2+1,WIDTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+gp.quicksum(x[i1,j1,k_dash1,i_dash2,j2,k_dash2,n,t] for k_dash1 in range(k1+1,HEIGHT) for i_dash2 in range(i2+1,WIDTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,1]*gp.quicksum(x[i_dash1,j1,k_dash1,i_dash2,j2,k_dash2,n,t] for i_dash1 in range(i1+1,WIDTH) for k_dash1 in range(0,HEIGHT) for i_dash2 in range(i2+1,WIDTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,2]*gp.quicksum(x[i1,j_dash1,k_dash1,i_dash2,j2,k_dash2,n,t] for j_dash1 in range(0,j1) for k_dash1 in range(0,HEIGHT) for i_dash2 in range(i2+1,WIDTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if j2>=j1:
                                            rightback_sum-=dir[t,0]*gp.quicksum(x[i_dash,j2,k_dash,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for i_dash in range(i2+1,WIDTH) for k_dash in range(0,HEIGHT))
                                        if j2<=j1:
                                            rightback_sum-=dir[t,2]*gp.quicksum(x[i_dash,j2,k_dash,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for i_dash in range(i2+1,WIDTH) for k_dash in range(0,HEIGHT))

                                        rear_sum=gp.quicksum(b[i2,j_dash,k_dash,n,t] for n in range(t+1,NBLOCK) for j_dash in range(0,j2) for k_dash in range(0,HEIGHT))+dir[t,0]*gp.quicksum(x[i1,j_dash1,k_dash1,i2,j_dash2,k_dash2,n,t] for j_dash1 in range(j1+1,DEPTH) for k_dash1 in range(0,HEIGHT) for j_dash2 in range(0,j2) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+gp.quicksum(x[i1,j1,k_dash1,i2,j_dash2,k_dash2,n,t] for k_dash1 in range(k1+1,HEIGHT) for j_dash2 in range(0,j2) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,2]*gp.quicksum(x[i1,j_dash1,k_dash1,i2,j_dash2,k_dash2,n,t] for j_dash1 in range(0,j1) for k_dash1 in range(0,HEIGHT) for j_dash2 in range(0,j2) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))+dir[t,1]*gp.quicksum(x[i_dash1,j1,k_dash1,i2,j_dash2,k_dash2,n,t] for i_dash1 in range(i1+1,WIDTH) for k_dash1 in range(0,HEIGHT) for j_dash2 in range(j2+1,DEPTH) for k_dash2 in range(0,HEIGHT) for n in range(t+1,NBLOCK))
                                        if i2>=i1:
                                            rear_sum-=dir[t,1]*gp.quicksum(x[i2,j_dash,k_dash,width,depth,height,n,t] for width in range(0,WIDTH) for depth in range(0,DEPTH) for height in range(0,HEIGHT) for n in range(t+1,NBLOCK) for j_dash in range(0,j2) for k_dash in range(0,HEIGHT))

                                        m.addConstr(front_sum<=(DEPTH-j2-1)*HEIGHT*front[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(front[i1,j1,k1,i2,j2,k2,t]<=front_sum)
                                        m.addConstr(rightback_sum<=(WIDTH-i2-1)*HEIGHT*rightback[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(rightback[i1,j1,k1,i2,j2,k2,t]<=rightback_sum)
                                        m.addConstr(rear_sum<=j2*HEIGHT*rear[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(rear[i1,j1,k1,i2,j2,k2,t]<=rear_sum)
                                        m.addConstr(rel_upp1[i1,j1,k1,i2,j2,k2,t]>=b_below+(1-front[i1,j1,k1,i2,j2,k2,t])-1)
                                        m.addConstr(rel_upp1[i1,j1,k1,i2,j2,k2,t]<=b_below)
                                        m.addConstr(rel_upp1[i1,j1,k1,i2,j2,k2,t]<=1-front[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(rel_right1[i1,j1,k1,i2,j2,k2,t]>=b_below+(1-rightback[i1,j1,k1,i2,j2,k2,t])-1)
                                        m.addConstr(rel_right1[i1,j1,k1,i2,j2,k2,t]<=b_below)
                                        m.addConstr(rel_right1[i1,j1,k1,i2,j2,k2,t]<=1-rightback[i1,j1,k1,i2,j2,k2,t])
                                        m.addConstr(rel_down1[i1,j1,k1,i2,j2,k2,t]>=b_below+(1-rear[i1,j1,k1,i2,j2,k2,t])-1)
                                        m.addConstr(rel_down1[i1,j1,k1,i2,j2,k2,t]<=b_below)
                                        m.addConstr(rel_down1[i1,j1,k1,i2,j2,k2,t]<=1-rear[i1,j1,k1,i2,j2,k2,t])
                                    m.addConstr(rel_upp[i1,j1,k1,i2,j2,k2,t]+rel_upp1[i1,j1,k1,i2,j2,k2,t]+rel_right[i1,j1,k1,i2,j2,k2,t]+rel_right1[i1,j1,k1,i2,j2,k2,t]+rel_down[i1,j1,k1,i2,j2,k2,t]+rel_down1[i1,j1,k1,i2,j2,k2,t]>=x_sum)


        # for i in range(0,WIDTH):
        #     for j in range(0,DEPTH):
        #             m.addConstr(b[i,j,15,0]==0)
        # m.addConstr(b[0,1,0,0] == 1)
        # m.addConstr(b[0,0,1,0] == 1)

        # m.addConstr(y[0,1,0,0] == 1)

        #初期値条件
        #3-6-15/1
        # m.addConstr(b[0,0,0,0,0] == 1)
        # m.addConstr(b[5,0,0,1,0] == 1)
        # m.addConstr(b[4,0,0,2,0] == 1)
        # m.addConstr(b[2,0,0,3,0] == 1)
        # m.addConstr(b[3,1,0,4,0] == 1)
        # m.addConstr(b[4,2,0,5,0] == 1)
        # m.addConstr(b[5,2,0,6,0] == 1)
        # m.addConstr(b[3,2,0,7,0] == 1)
        # m.addConstr(b[2,1,0,8,0] == 1)
        # m.addConstr(b[4,1,0,9,0] == 1)
        # m.addConstr(b[5,1,0,10,0] == 1)
        # m.addConstr(b[2,2,0,11,0] == 1)
        # m.addConstr(b[3,0,0,12,0] == 1)
        # m.addConstr(b[1,1,0,13,0] == 1)
        # m.addConstr(b[1,0,0,14,0] == 1)
        # m.addConstr(b[3,0,1,15,0] == 1)

        # m.addConstr(b[0,1,0,14,0] == 0)
        # m.addConstr(b[1,2,0,14,0] == 0)
        # m.addConstr(b[1,2,0,15,0] == 0)
        # for i in range(0,WIDTH):
        #     for j in range(0,DEPTH):
        #         m.addConstr(b[i,j,1,14,0] == 0)

        # m.addConstr(y[0,0,0,0,0] == 1)

        #4-6-23/700
        # m.addConstr(b[3,2,0,0,0] == 1)
        # m.addConstr(b[4,1,0,1,0] == 1)
        # m.addConstr(b[2,3,0,2,0] == 1)
        # m.addConstr(b[3,1,0,3,0] == 1)
        # m.addConstr(b[0,0,0,4,0] == 1)
        # m.addConstr(b[3,0,0,5,0] == 1)
        # m.addConstr(b[2,2,0,6,0] == 1)
        # m.addConstr(b[5,3,0,7,0] == 1)
        # m.addConstr(b[0,1,0,8,0] == 1)
        # m.addConstr(b[5,2,0,9,0] == 1)
        # m.addConstr(b[4,0,0,10,0] == 1)
        # m.addConstr(b[0,3,0,11,0] == 1)
        # m.addConstr(b[5,1,0,12,0] == 1)
        # m.addConstr(b[0,2,0,13,0] == 1)
        # m.addConstr(b[2,1,0,14,0] == 1)
        # m.addConstr(b[1,0,0,15,0] == 1)
        # m.addConstr(b[1,1,0,16,0] == 1)
        # m.addConstr(b[1,2,0,17,0] == 1)
        # m.addConstr(b[4,2,0,18,0] == 1)
        # m.addConstr(b[2,0,0,19,0] == 1)
        # m.addConstr(b[3,3,0,20,0] == 1)
        # m.addConstr(b[4,3,0,21,0] == 1)
        # m.addConstr(b[5,0,0,22,0] == 1)

        # m.addConstr(y[3,2,0,0,0] == 1)

        #初期値条件
        (1)
        filename = "../Benchmark3D/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(HEIGHT) + "-" + str(NBLOCK)+ "/" + str(index).zfill(5) + ".txt"
        print(filename)
        file = open(filename, "r")
        block=[
        [
            [0 for _ in range(DEPTH)]  # 4要素の1次元配列を3つ持つ2次元配列
            for _ in range(WIDTH)  # 3つの1次元配列を持つ1次元配列
        ]
        for _ in range(HEIGHT)  # 3つの2次元配列を持つ1次元配列
    ]   
        for k in range(0,HEIGHT):
            print("k=",k)
            for i in range(0,WIDTH):
                line = file.readline()
                element = line.split()
                for j in range(0,DEPTH):
                    block[k][i][j]=int(element[j])
                    print("{:2}".format(element[j])+" ",end=' ')
                print()
            line=file.readline()
            print("")
        file.close()
        for k in range(0,HEIGHT):
            for i in range(0,WIDTH):
                for j in range(0,DEPTH):
                    if(block[k][i][j]!=0):
                        m.addConstr(b[i,j,k,block[k][i][j]-1,0]==1)
                    else:
                        m.addConstr(b[i,j,k,NBLOCK-1,0]==0)
                

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
            filename = "../Benchmark3D/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(HEIGHT) + "-" + str(NBLOCK)+ "(ip2s_3D)"+".csv"
            w_file=open(filename,"w")
        w_file.write(str(opt))
        w_file.write("\n")

        if index%100 == 0:
            NBLOCK+=1
            w_file.close()

    break


print("optimal_value:",sum_opt/(100*DEPTH-timeup),"average time:",total_time/(100*DEPTH-timeup),"max time:",max_time,"timeup:",timeup)

#決定変数の値を表示
for t in range(0,NBLOCK):
    print("t=",t+1)
    block=[
        [
            [0 for _ in range(DEPTH)]  # 4要素の1次元配列を3つ持つ2次元配列
            for _ in range(WIDTH)  # 3つの1次元配列を持つ1次元配列
        ]
    for _ in range(HEIGHT)  # 3つの2次元配列を持つ1次元配列
    ]
    for n in range(t,NBLOCK):
        for i in range(0,WIDTH):
            for j in range(0,DEPTH):
                for k in range(0,HEIGHT):
                    if b[i,j,k,n,t].x==1:
                        block[k][i][j]=n+1
    for k in range(0,HEIGHT):
        print("k=",k)
        for j in range(DEPTH-1,-1,-1):
            for i in range(0,WIDTH):
                print("{:2}".format(block[k][i][j]),end=" ")
            print("")
    for n in range(t+1,NBLOCK):
        for i1 in range(0,WIDTH):
            for j1 in range(0,DEPTH):
                for k1 in range(0,HEIGHT):
                    for i2 in range(0,WIDTH):
                        for j2 in range(0,DEPTH):
                            for k2 in range(0,HEIGHT):
                                if x[i1,j1,k1,i2,j2,k2,n,t].x==1:
                                    print("(",i1,j1,k1,")","(",i2,j2,k2,")",n+1)
                                    print("rel_upp=",rel_upp[i1,j1,k1,i2,j2,k2,t].x)
                                    print("rel_upp1=",rel_upp1[i1,j1,k1,i2,j2,k2,t].x)
                                    print("rel_right=",rel_down[i1,j1,k1,i2,j2,k2,t].x)
                                    print("rel_right1=",rel_down1[i1,j1,k1,i2,j2,k2,t].x)


