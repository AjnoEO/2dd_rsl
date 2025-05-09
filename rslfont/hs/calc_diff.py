from functools import lru_cache
import numpy as np
import os
import pandas as pd
import re

vertices: set[str] = set()
vertex_copies: dict[str, list[str]] = {}
edges: dict[tuple[str, str], int] = {}
hooks: dict[str, str] = {}

@lru_cache
def analyze_vertex(v: str):
    hss = v.split(",")
    v0 = hss.pop(0)
    if len(hss) > 0 and v0 not in vertex_copies:
        vertex_copies[v0] = hss
    return v0

with open(os.path.join("rslfont", "hs", "edges.txt"), encoding="utf8") as f:
    for line in f:
        match = re.match(r"(\S+) (-[>-]) (\S+)(?: (\d))?", line)
        if not match:
            raise SyntaxError(f"Не могу распарсить ребро {line}")
        v1, edge, v2 = match.group(1, 2, 3)
        w = int(match.group(4) or 0)
        v1 = analyze_vertex(v1)
        v2 = analyze_vertex(v2)
        vertices.add(v1)
        vertices.add(v2)
        if w:
            edges[(v1, v2)] = w
        if edge == "->":
            hooks[v2] = v1

def calc_diff(*arrays: np.ndarray):
    v1, v2 = [vertices[int(a[0])] for a in arrays]
    w = edges.get((v1, v2)) or edges.get((v2, v1)) or 0
    return 3 - w

vertices = sorted(vertices)
HS = pd.DataFrame(range(len(vertices)), index=pd.Index(vertices, name="HS"))
print(HS.head())
pairwise_similarity = HS.T.corr(calc_diff).astype(np.int8)
pairwise_similarity -= pd.DataFrame(np.identity(HS.shape[0], dtype=np.int8), index=HS.index, columns=HS.index)
for v, copies in vertex_copies.items():
    for c in copies:
        pairwise_similarity.loc[c] = pairwise_similarity.loc[v]
        pairwise_similarity[c] = pairwise_similarity[v]
pairwise_similarity.to_csv(os.path.join("rslfont", "hs", "diff.tsv"), sep="\t")

pd.Series(hooks).to_csv(os.path.join("rslfont", "hs", "hooks.tsv"), sep="\t", header=False)

print(vertices, vertex_copies, edges, sep="\n")
