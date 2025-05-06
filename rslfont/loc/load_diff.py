import os
import pandas as pd
import numpy as np
from ..regexes import HS

LOC_DIFF = pd.read_csv(os.path.join("rslfont", "loc", "diff.tsv"), index_col=0, sep="\t").astype(np.int8)

def uniform_loc(loc: str):
    if not loc: return loc
    if "Й" in loc: return None
    return loc.replace(HS, 'h')

def loc_difference(loc1: str, loc2: str):
    """
    Разница между локализациями
    - `0`: отсутствует или пренебрежимо мала
    - `1`: мала
    - `2`: велика
    """
    loc1, loc2 = uniform_loc(loc1), uniform_loc(loc2)
    if not loc1 and not loc2: return 0
    if not loc1 or not loc2: return 1
    return LOC_DIFF.loc[loc1, loc2]

if __name__ == "__main__":
    print(loc_difference("(.)", "(..)"), loc_difference("(.)", "(...)"), loc_difference("(.)", "9.0"))
