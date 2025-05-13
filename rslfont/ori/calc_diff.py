import json
import numpy as np
import os
import pandas as pd

with open(os.path.join("rslfont", "ori", "edges.json"), encoding="utf8") as f:
    data: dict[str, dict[str, list[str]]] = json.load(f)

oris = np.array([[f+c, c+f] for f in '.Ё' for c in '%ЖЭ-"=']).flatten()
n = len(oris)

table = (np.ones((n, n))-np.identity(n))*3
table = table.astype(np.int8)
df = pd.DataFrame(table, index=oris, columns=oris)

for ori, linked in data.items():
    for i in range(1, 3):
        for ori2 in linked[str(i)]:
            if df.loc[ori, ori2] not in (i, 3): raise Exception(f"Противоречивые данные о связи {ori} и {ori2}")
            df.loc[ori, ori2] = df.loc[ori2, ori] = i

df.to_csv(os.path.join("rslfont", "ori", "diff.tsv"), sep="\t", quotechar="'")
