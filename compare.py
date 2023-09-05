import pandas as pd

DEPTH=3
WIDTH=6
NBLOCK=17

filename_a = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "(ip3)"+".csv"
filename_b = "../Benchmark/" + str(DEPTH) + "-" + str(WIDTH) + "-" + str(NBLOCK)+ "(bb3)"+".csv"

# CSVファイルの読み込み
df_a = pd.read_csv(filename_a)
df_b = pd.read_csv(filename_b)

# 行ごとに数値を比較
row_comparison = df_a == df_b  # 各要素を比較し、同じ値の場合はTrue、異なる場合はFalse

# 各行の比較結果を表示
for index, row in row_comparison.iterrows():
    if not row.all():  # 行内のすべての要素がTrueの場合、行全体が一致しているとみなす
        print(f"行 {index + 1} は一致していない。")
