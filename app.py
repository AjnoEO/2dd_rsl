from flask import Flask, g, render_template, redirect, url_for, request, session
import re
from functools import wraps
import dictionary as d
from security import FLASK_SECRET_KEY, check_password

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("editor", False):
            return f(*args, **kwargs)
        return redirect(url_for('editor_login', next=request.full_path))
    return decorated_function

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

@app.route("/edit")
@login_required
def edit():
    return render_template("edit.html", dictionary_html=d.dict_html())

@app.route("/edit/login", methods=["GET", "POST"])
def editor_login():
    error = None
    if request.method == 'POST':
        if check_password(request.form["password"]):
            session["editor"] = True
            return redirect(request.form.get("next") or url_for("edit"))
        else:
            error = "Неправильный пароль"
    return render_template("editor_login.html", error=error)

@app.route("/edit/logout", methods=["GET", "POST"])
def editor_logout():
    session.pop("editor")
    return redirect(request.args.get("next") or url_for("index"))
