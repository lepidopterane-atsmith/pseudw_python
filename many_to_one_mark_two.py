import pandas as pd

files = ["bow_results_0001-001.csv", "bow_results_0005-001.csv", "bow_results_0007-005.csv", "bow_results_0012-001.csv", "bow_results_0012-002.csv", "bow_results_0019-002.csv", "bow_results_0023-001.csv", "bow_results_0024-001.csv", "bow_results_0032-014.csv", "bow_results_0033-002.csv", "bow_results_0062-033.csv", "bow_results_0062-037.csv", "bow_results_0062-063.csv", "bow_results_0062-068.csv", "bow_results_0081-005.csv", "bow_results_0081-009.csv", "bow_results_0081-010.csv", "bow_results_0341-002.csv", "bow_results_0545-001.csv", "bow_results_0559-002.csv", "bow_results_0627-022.csv", "bow_results_0719-001.csv", "bow_results_2042-001.csv"]

dfs = pd.concat([pd.read_csv(i) for i in files])

csv_full = dfs.to_csv("bow_results.csv", index=False)

print("*~ and now a nice dataframe ~*")

