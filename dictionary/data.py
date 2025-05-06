import os
import pandas as pd

DICT_PATH = os.path.join("dictionary", "dict.tsv")
DICT = pd.read_csv(DICT_PATH, sep='\t', quotechar="'")

def update_dict():
    DICT.to_csv(DICT_PATH, sep='\t')