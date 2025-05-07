import pandas as pd
from rslfont import sign_difference
from .data import DICT
from .classes import Lexeme

def lexemes_from_relevant_rows(results: pd.DataFrame):
    results.fillna({"Lemma": results["RSL"]}, inplace=True)
    lemmas = results["Lemma"].drop_duplicates()
    search_results = [Lexeme(DICT[(DICT["Lemma"] == lemma) | (DICT["RSL"] == lemma)]) for lemma in lemmas]
    return search_results

def search_for_lexemes(query: str, exact: bool = False):
    if exact:
        results = DICT[DICT["RSL"] == query]
    else:
        similarity = DICT["RSL"].apply(lambda sign: sign_difference(sign, query)).rename("similarity")
        results = pd.concat([DICT, similarity], axis="columns")
        results.sort_values(by=["similarity"], inplace=True)
        results = results[results["similarity"] < 3]
    return lexemes_from_relevant_rows(results)
