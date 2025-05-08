from bs4 import BeautifulSoup
import os
import pandas as pd
from flask import render_template, url_for
from functools import partial

DICT_PATH = os.path.join("dictionary", "dict.tsv")
DICT = pd.read_csv(DICT_PATH, sep='\t', quotechar="'", dtype="str")

def __delete_button(id: int):
    return render_template(
        "dialog_template.html", id=f"delete_{id}", action=url_for("delete_word", word_index=id), confirm_text="Удалить",
        text_html=(
            f'Запись <span class="rsl">{DICT.loc[id, "RSL"]}</span> ({DICT.loc[id, "Russian"]}) '
            'будет удалена <strong>безвозвратно</strong>.'
        )
    )

def __format_cell(contents: str, col: str):
    if col == "Edit":
        return render_template("edit_edit_button.html", id=contents)
    if col == "Delete":
        return render_template("edit_delete_button.html", id=contents) + '\n' + __delete_button(contents)
    if col in ["Russian", "GrammarMeaning"]:
        contents = contents.replace(";", "<br>")
    classes = []
    if col in ["RSL", "Lemma", "Example_RSL"]:
        classes += ["compact", "rsl"]
    classes = " ".join(classes)
    if not classes: return contents
    return f'<span class="{classes}">{contents}</span>'

def dict_html():
    index_series = DICT.index.to_series()
    table = pd.concat([DICT, index_series.rename("Edit"), index_series.rename("Delete")], axis='columns')
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