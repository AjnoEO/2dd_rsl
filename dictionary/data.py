from bs4 import BeautifulSoup
import os
import pandas as pd
from functools import partial

DICT_PATH = os.path.join("dictionary", "dict.tsv")
DICT = pd.read_csv(DICT_PATH, sep='\t', quotechar="'", dtype="str")

def __format_cell(contents: str, col: str):
    if col == "Edit":
        return f'<a class="small circle transparent button" href="/edit/{contents}"><i class="small">edit</i></a>'
    if col in ["Russian", "GrammarMeaning"]:
        contents = contents.replace(";", "<br>")
    classes = []
    if col in ["RSL", "Lemma", "Example_RSL"]:
        classes += ["compact", "rsl"]
    classes = " ".join(classes)
    if not classes: return contents
    return f'<span class="{classes}">{contents}</span>'

def dict_html():
    table = pd.concat([DICT, DICT.index.to_series(name="Edit")], axis='columns')
    html = table.to_html(
        index=False, classes="", justify="center", border=0, escape=False, render_links=True, na_rep='&mdash;',
        formatters={col: partial(__format_cell, col=col) for col in table.columns}
    )
    htmlsoup = BeautifulSoup(html, "lxml")
    htmlsoup.find("thead")["class"] = ["fixed", "fill"]
    for cell in htmlsoup("td", string="—"):
        cell["class"] = ["surface-variant", "center-align"]
    return htmlsoup

def update_dict():
    DICT.to_csv(DICT_PATH, sep='\t', quotechar="'", index=False)