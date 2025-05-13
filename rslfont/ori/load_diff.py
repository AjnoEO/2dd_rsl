import os
import pandas as pd
import numpy as np

ORI_DIFF = pd.read_csv(os.path.join("rslfont", "ori", "diff.tsv"), index_col=0, sep="\t", quotechar="'").astype(np.int8)

def ori_difference(ori1: str, ori2: str, hand: str = "r"):
    """
    Разница между ориентациями
    - `None`: ori1 и ori2 — None
    - `0`: отсутствует 
    - `1`: мала
    - `2`: достаточно мала
    - `3`: велика
    """
    if hand == "l":
        if ori1: ori1 = ori1[::-1]
        if ori2: ori2 = ori2[::-1]
    if not ori1 and not ori2: return None
    if not ori1 or not ori2: return 0
    return ORI_DIFF.loc[ori1, ori2]

if __name__ == "__main__":
    print(ori_difference(".Э", "-."), ori_difference(".Э", "-.", hand="l"))
