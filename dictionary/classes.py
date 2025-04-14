import pandas as pd
import numpy as np
from .utils import category_values_order, url_root

class UntreatableLexemeException(Exception): ...

class Lexeme:
    def __init__(self, rows: pd.DataFrame):
        head = rows[rows["Lemma"].isna() | (rows["RSL"] == rows["Lemma"])]
        lemma, translations, sources = (head[col] for col in ["RSL", "Russian", "Sources"])
        self.lemma: str = lemma.iloc[0]
        self.translations: list[list[str]] = [t.split(";") for t in translations]
        sources = [
            tuple(item.split("=", 1)[::-1]) if "=" in item else (item, self.translations[i][0])
            for i, s in enumerate(sources) if s is not np.nan for item in s.split(" ")
        ]
        self.sources: dict[str, list[tuple[str, str]]] = {}
        for url, translation in sources:
            self.sources.setdefault(url_root(url), []).append((url, translation))
        for source, links in self.sources.items():
            links.sort(key = lambda t: t[1])
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
            UntreatableLexemeException(f"Too many grammatical categories per lexeme: {self.lemma}")
