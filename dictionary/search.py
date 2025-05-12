import pandas as pd
from rslfont import sign_difference
from .data import DICT
from .classes import Lexeme

def lexemes_from_relevant_rows(results: pd.DataFrame):
    results.fillna({"Lemma": results["RSL"]}, inplace=True)
    lemmas = results[["RSL", "Lemma"]].drop_duplicates("Lemma")
    search_results = [
        (Lexeme(DICT[(DICT["Lemma"] == lemma) | (DICT["RSL"] == lemma)]), bool(word == lemma)) 
        for (word, lemma) in lemmas.itertuples(index=False)]
    return search_results

def search_for_lexemes(query: str, exact: bool = False):
    """Возвращает список кортежей (*Лемма*, [является ли нач. форма результатом поиска])"""
    if exact:
        results = DICT[DICT["RSL"] == query]
    else:
        similarity = DICT["RSL"].apply(lambda sign: sign_difference(sign, query)).rename("similarity")
        results = pd.concat([DICT, similarity], axis="columns")
        results = results[results["similarity"] < 3]
        results.sort_values(by=["similarity"], inplace=True)
    return lexemes_from_relevant_rows(results)

def __consider_brackets(text: str):
    if "(" not in text: return [text]
    o = text.find("(")
    c = text.rfind(")")
    before, inside, after = text[:o], text[o+1:c], text[c+1:]
    return [" ".join((before + after).split()), before + inside + after]

def __translation_match(query: str, translations: str):
    """Насколько перевод соответствует запросу. `4` = не соответствует"""
    translations = translations.split(";")
    match_i = 4
    for raw_tr in translations:
        for tr in __consider_brackets(raw_tr):
            i = (
                0 if tr == query else
                1 if tr.startswith(query) else
                2 if tr.endswith(query) else
                3 if query in tr else
                4
            )
            match_i = min(match_i, i)
    return match_i

def search_for_translations(query: str):
    """Возвращает список кортежей (*Лемма*, `True`)"""
    similarity = DICT["Russian"].fillna("").apply(lambda trs: __translation_match(query, trs)).rename("similarity")
    results = pd.concat([DICT, similarity], axis="columns")
    results = results[results["similarity"] < 4]
    results.sort_values(by=["similarity"], inplace=True)
    return lexemes_from_relevant_rows(results)