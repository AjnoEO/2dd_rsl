import pandas as pd

class Lexeme:
    def __init__(self, rows = pd.DataFrame):
        self.lemma, self.translations, self.sources = \
            rows[rows["Lemma"].isna() | (rows["RSL"] == rows["Lemma"])].loc[0, ["RSL", "Russian", "Sources"]]
        self.lemma: str
        self.translations: list[str] = self.translations.split(";")
        self.sources: list[str] = self.sources.split(" ")
        self.gram_forms = None
        if rows.shape[0] == 1:
            return
        self.gram_forms = {}
        self.gram_categories = {} # {S: [None я ты он], O: [мне тебе ему]}
