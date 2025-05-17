import os
import pandas as pd
import numpy as np

HS_DIFF = pd.read_csv(os.path.join("rslfont", "hs", "diff.tsv"), sep="\t", index_col="HS").astype(np.int8)
HOOKS = pd.read_csv(os.path.join("rslfont", "hs", "hooks.tsv"), sep="\t", index_col=0, header=None, dtype="str")[1].to_dict()

def hs_difference(hs1: str, hs2: str, allow_hooks: bool = False) -> int | None:
    """
    Разница между конфигурациями
    - `None`: hs1 и hs2 — None
    - `0`: отсутствует
    - `1`: пренебрежимо мала
    - `2`: мала
    - `3`: велика
    """
    if not hs1 and not hs2: return None
    if not hs1 or not hs2: return 3
    diff = HS_DIFF.loc[hs1, hs2]
    if allow_hooks:
        if straight := HOOKS.get(hs1): diff = min(diff, HS_DIFF.loc[straight, hs2])
        if straight := HOOKS.get(hs2): diff = min(HS_DIFF.loc[hs1, straight], diff)
    return diff

if __name__ == "__main__":
    print(hs_difference("к", "п"), hs_difference("а", "6"), hs_difference("ж", "ф"))
