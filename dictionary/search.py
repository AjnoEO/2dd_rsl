import pandas as pd
from rslfont import sign_difference
from .data import DICT
from .classes import Lexeme

def search_for_lexemes(query: str):
    similarity = DICT["RSL"].apply(lambda sign: sign_difference(sign, query)).rename("similarity")
    results = pd.concat([DICT, similarity], axis="columns")
    results.sort_values(by=["similarity"], inplace=True)
    results = results[results["similarity"] < 3]
    results.fillna({"Lemma": results["RSL"]}, inplace=True)
    lemmas = results["Lemma"].drop_duplicates()
    search_results = [Lexeme(DICT[(DICT["Lemma"] == lemma) | (DICT["RSL"] == lemma)]) for lemma in lemmas]
    return search_results
