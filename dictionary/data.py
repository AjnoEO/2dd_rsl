from bs4 import BeautifulSoup
import os
import pandas as pd
from functools import partial

DICT_PATH = os.path.join("dictionary", "dict.tsv")
DICT = pd.read_csv(DICT_PATH, sep='\t', quotechar="'")

def __format_cell(contents: str, col: str):
    if col in ["Russian", "GrammarMeaning"]:
        contents = contents.replace(";", "<br>")
    classes = []
    if col in ["RSL", "Lemma", "Example_RSL"]:
        classes.append("rsl")
    classes = " ".join(classes)
    if not classes: return contents
    return f'<span class="{classes}">{contents}</span>'

def dict_html():
    html = DICT.to_html(
        index=False, classes="", justify="center", border=0, escape=False, render_links=True, na_rep='',
        formatters={col: partial(__format_cell, col=col) for col in DICT.columns}
    )
    htmlsoup = BeautifulSoup(html, "lxml")
    htmlsoup.find("thead")["class"] = ["fixed", "fill"]
    return htmlsoup

def update_dict():
    DICT.to_csv(DICT_PATH, sep='\t')