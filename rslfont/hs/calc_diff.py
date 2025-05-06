from functools import lru_cache
import numpy as np
import os
import pandas as pd
from .load_info import HS, HSTuple, hs_tuple

def invert(hs: HSTuple) -> HSTuple:
    return HSTuple(hs.selected ^ 0b1111, *[-v for v in hs[1:5]], hs.dispersed, hs.thumb)

@lru_cache
def __helper_difference(hs1_tuple: HSTuple, hs2_tuple: HSTuple, log: bool = False) -> int:
    """`0` - no diff, `1` - negligible diff, `2` - small diff, `3` - large diff"""
    hs1 = np.array(hs1_tuple, dtype=np.int8)
    hs2 = np.array(hs2_tuple, dtype=np.int8)
    if (hs1[1:5] == -1).sum() == 2 or (hs2[1:5] == -1).sum() == 2:
        return 3
    dispersedness_diff = int(hs1[5] * hs2[5] == -1)
    result = dispersedness_diff
    thumb_diff = abs(hs1[6] - hs2[6])
    result += 0 if thumb_diff == 0 else 1 if thumb_diff <= 2 else 2
    shape_sum = hs1[1:5] + hs2[1:5]
    same_base = -2 in shape_sum or -1 not in hs1[1:5] or -1 not in hs2[1:5]
    similar_base = (
        hs1[1] == hs2[1] == -1
        or hs1[4] == hs2[4] == -1
        or (hs1[4] != -1 and hs2[4] != -1 and hs1[6] <= 1 and hs2[6] <= 1) # thumb contacting base fingers
        or (hs1[1] != -1 and hs2[1] != -1 and hs1[6] >= 2 and hs2[6] >= 2) # thumb not contacting base fingers
    )
    same_selected = 1 not in shape_sum or 1 not in hs1[1:5] or 1 not in hs2[1:5]
    similar_selected = (
        hs1[1] == hs2[1] == 1
        or hs1[4] == hs2[4] == 1
        or (hs1[4] != 1 and hs2[4] != 1 and hs1[6] <= 1 and hs2[6] <= 1) # thumb contacting selected fingers
        or (hs1[1] != 1 and hs2[1] != 1 and hs1[6] >= 2 and hs2[6] >= 2) # thumb not contacting selected fingers
    )
    result += (
        0 if same_base and same_selected
        else 1 if (same_base and similar_selected) or (same_selected and similar_base)
        else 3
    )
    selected_diff = (hs1[0] ^ hs2[0]).bit_count()
    result += (
        3 if not (same_base or similar_base)
        else 0 if selected_diff == 0
        else 1 if selected_diff == 1 and (hs1[0].bit_count() != 0) and (hs2[0].bit_count() != 0)
        else 1 if {hs1[0], hs2[0]} == {0b1111, 0b0011} or {hs1[0], hs2[0]} == {0b0000, 0b1100}
        else 3
    )
    if log:
        print(hs1_tuple, hs2_tuple, result)
        print(selected_diff, same_base, similar_base, same_selected, similar_selected, dispersedness_diff, thumb_diff)
        # print({hs1[0], hs2[0]}, {0b1111, 0b1100}, {0b0000, 0b0011})
    return min(result, 3)

@lru_cache
def difference(hs1: HSTuple, hs2: HSTuple) -> int:
    antihs1 = invert(hs1)
    return min(__helper_difference(hs1, hs2), __helper_difference(antihs1, hs2))

print(HS)
print(HS.dtypes)

def calc_diff(*arrays: np.ndarray):
    hstuples = [HSTuple(*arr.astype(np.int8)) for arr in arrays]
    return difference(*hstuples)

pairwise_similarity = HS.T.corr(calc_diff).astype(np.int8)
pairwise_similarity -= pd.DataFrame(np.identity(HS.shape[0], dtype=np.int8), index=HS.index, columns=HS.index)
pairwise_similarity.to_csv(os.path.join("rslfont", "hs", "diff.tsv"), sep="\t")
# print(pairwise_similarity)

for l in HS.index:
    print(l)
    for i in range(3):
        print(f"{i}:", *pairwise_similarity[pairwise_similarity[l]==i].index)

l1 = "И"
l2 = "М"
print(f"{l1} - {l2}")
l1tuple = hs_tuple(l1)
l2tuple = hs_tuple(l2)
__helper_difference(l1tuple, l2tuple, log=True)
__helper_difference(invert(l1tuple), l2tuple, log=True)
