import pandas as pd
import numpy as np
from .utils import category_values_order

class UntreatableLexemeException(Exception): ...

class Lexeme:
    def __init__(self, rows = pd.DataFrame):
        self.lemma, self.translations, self.sources = \
            rows[rows["Lemma"].isna() | (rows["RSL"] == rows["Lemma"])].reset_index().loc[0, ["RSL", "Russian", "Sources"]]
        self.lemma: str
        self.translations: list[str] = self.translations.split(";")
        self.sources: list[str] = self.sources.split(" ") if self.sources is not np.nan else []
        if rows.shape[0] == 1:
            return
        self.inflection: list[dict[str, str | list[str]]] = [] # list of rows: [{"title", "value"}] or [{"title", "values"}]
        self.inflection_columns: list[str] | None = None
        categories: dict[str, set[str]] = {}
        catval_to_word: dict[str, str] = {}
        for word in rows.itertuples(index=False):
            if word.Lemma is np.nan: continue
            cat_val: list[str] = sorted(word.GrammarMeaning.split(";"))
            catval_to_word[";".join(cat_val)] = word.RSL
            cat_val: dict[str, str] = dict([tuple(cv.split(":")) for cv in cat_val])
            if not categories:
                categories = {cat: {val} for cat, val in cat_val.items()}
            else:
                for cat, val in cat_val.items():
                    categories.setdefault(cat, {""})
                    categories[cat].add(val)
        for cat in categories:
            categories[cat] = sorted(categories[cat], key = lambda value: (category_values_order(value), value))
        self.inflection_dim: int = len(categories)           
        if self.inflection_dim == 1:
            cat, rows = categories.popitem()
            for row in rows:
                self.inflection.append({
                    "title": row,
                    "value": catval_to_word[f"{cat}:{row}"]
                })
        elif self.inflection_dim == 2:
            cats = sorted(categories.items(), key = lambda i: len(i[1]))
            colcat = cats[0][0]
            rowcat = cats[1][0]
            self.inflection_columns = categories[colcat]
            for row in categories[rowcat]:
                self.inflection.append({
                    "title": row,
                    "columns": [
                        catval_to_word.get(";".join(sorted([f"{rowcat}:{row}", f"{colcat}:{col}"])))
                        for col in categories[colcat]
                    ]
                })
        else:
            UntreatableLexemeException("Too many grammatical categories per lexeme")
