import os
import pandas as pd
import numpy as np

HS_DIFF = pd.read_csv(os.path.join("rslfont", "hs", "diff.tsv"), sep="\t", index_col="HS").astype(np.int8)

def hs_difference(hs1: str, hs2: str):
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
    return HS_DIFF.loc[hs1, hs2]

if __name__ == "__main__":
    print(hs_difference("к", "п"), hs_difference("а", "6"), hs_difference("ж", "ф"))
