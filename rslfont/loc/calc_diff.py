import json
import numpy as np
import os
import pandas as pd

with open(os.path.join("rslfont", "loc", "loc.json"), encoding="utf8") as f:
    data: dict[str, dict[str, list[str]]] = json.load(f)

locs = []
for loc, linked in data.items():
    if loc not in locs: locs.append(loc)
    for linked_locs in linked.values():
        for l_loc in linked_locs:
            if l_loc not in locs: locs.append(l_loc)

n = len(locs)
table = (np.ones((n, n))-np.identity(n))*2
table = table.astype(np.int8)
df = pd.DataFrame(table, index=locs, columns=locs)

for loc, linked in data.items():
    for i in range(2):
        if str(i) not in linked: continue
        for loc2 in linked[str(i)]:
            if df.loc[loc, loc2] not in (i, 2): raise Exception(f"Противоречивые данные о связи {loc} и {loc2}")
            df.loc[loc, loc2] = df.loc[loc2, loc] = i

df.to_csv(os.path.join("rslfont", "loc", "diff.tsv"), sep="\t")
