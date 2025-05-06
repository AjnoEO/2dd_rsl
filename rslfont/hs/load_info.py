from collections import namedtuple
import os
import pandas as pd
import numpy as np

HS_PATH = os.path.join("rslfont", "hs", "hs.tsv")
HS = pd.read_csv(HS_PATH, sep='\t', index_col='HS', dtype={
    'selected': str,
    'closed': np.int8,
    'hook': np.int8,
    'forward': np.int8,
    'straight': np.int8,
    'dispersed': np.int8,
    'thumb': np.int8
})
def selected_to_enum(input: str) -> int:
    if input == '0': return 0
    result = 0
    for i in input:
        result += 1 << (int(i) - 2)
    return result
HS['selected'] = HS['selected'].apply(selected_to_enum).astype(np.int8)
HSTuple = namedtuple("HS", ["selected", "closed", "hook", "forward", "straight", "dispersed", "thumb"])

def hs_tuple(hs: str):
    return HSTuple(*HS.loc[hs])