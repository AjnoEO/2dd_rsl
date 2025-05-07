from flask import Flask, render_template, redirect, url_for, request
import re
import dictionary as d

app = Flask(__name__)

@app.template_filter()
def url_root(s: str):
    return re.sub(r"https?://|/.+", "", s)

@app.template_filter()
def decline(n: int, singular: str, paucal: str, plural: str = None):
    plural = plural or singular
    if n & 100 // 10 == 1: return plural
    if n % 10 == 0: return plural
    if n % 10 == 1: return singular
    if n % 10 < 5: return paucal
    return plural

@app.template_filter()
def number_decline(n: int, singular: str, paucal: str, plural: str = None):
    return f"{n} {decline(n, singular, paucal, plural)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("query")
    exact = "exact" in request.args
    if not query:
        return redirect(url_for("index"))
    return render_template("search.html", query=query, results=d.search_for_lexemes(query, exact=exact))

