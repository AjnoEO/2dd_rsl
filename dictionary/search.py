import pandas as pd
from .data import DICT
from .classes import Lexeme

def search_for_lexemes(query: str):
    results = pd.concat([
        DICT[DICT["RSL"] == query], 
        DICT[DICT["RSL"].str.contains(query, regex=False)]
    ], axis="index")
    results.drop_duplicates(inplace=True)
    results.fillna({"Lemma": results["RSL"]}, inplace=True)
    lemmas = results["Lemma"].unique()
    search_results = [Lexeme(DICT[(DICT["Lemma"] == lemma) | (DICT["RSL"] == lemma)]) for lemma in lemmas]
    return search_results
