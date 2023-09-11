import pandas as pd

DEPTH=3
WIDTH=8
NBLOCK=23

filename_a = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "(ip2d)"+".csv"
filename_b = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "(bb2d)"+".csv"

# CSVファイルの読み込み
df_a = pd.read_csv(filename_a)
df_b = pd.read_csv(filename_b)

# 行ごとに数値を比較し、df_aの値が-1の行をスキップする
for index, row_a in df_a.iterrows():
    if row_a.iloc[0] == -1:  # 列名を実際の列名に置き換える
        continue  # df_aの値が-1の行はスキップ
    row_b = df_b.iloc[index]  # df_bから同じ行を取得
    row_comparison = (row_a == row_b)
    
    if not row_comparison.all():
        print(f"行 {index + 2} は一致していません。")
