from flask import Flask, abort, render_template, redirect, url_for, request, session
import re
from functools import wraps
import dictionary as d
from rslfont import FrameParsingError
from security import FLASK_SECRET_KEY, IS_PRODUCTION, check_password
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
if IS_PRODUCTION:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.template_filter()
def url_root(s: str):
    return re.sub(r"https?://|/.+", "", s)

@app.template_filter()
def decline(n: int, singular: str, paucal: str, plural: str | None = None):
    plural = plural or singular
    if n & 100 // 10 == 1: return plural
    if n % 10 == 0: return plural
    if n % 10 == 1: return singular
    if n % 10 < 5: return paucal
    return plural

@app.template_filter()
def number_decline(n: int, singular: str, paucal: str, plural: str | None = None):
    return f"{n} {decline(n, singular, paucal, plural)}"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("editor", False):
            return f(*args, **kwargs)
        return redirect(url_for('editor_login', next=request.full_path))
    return decorated_function

@app.errorhandler(404)
def page_not_found(error: Exception):
    return render_template("error_404.html", error=error), 404

@app.errorhandler(FrameParsingError)
def frame_parsing_error(error: FrameParsingError):
    return render_template("error_400_parse_frame.html", error=error, query=request.args.get("query")), 400

@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='favicon.ico')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("query")
    exact = "exact" in request.args
    translations = "translations" in request.args
    if not query:
        return redirect(url_for("index"))
    if translations:
        results = d.search_for_translations(query)
    else:
        results = d.search_for_lexemes(query, exact=exact)
    return render_template("search.html", query=query, results=results)

@app.route("/edit/")
@login_required
def edit():
    return render_template("edit.html", dictionary_html=d.dict_html())

@app.route("/edit/login", methods=["GET", "POST"])
def editor_login():
    if session.get("editor"): return redirect(request.args.get("next") or url_for("edit"))
    error = None
    if request.method == 'POST':
        if check_password(request.form["password"]):
            session["editor"] = True
            return redirect(request.form.get("next") or url_for("edit"))
        else:
            error = "Неправильный пароль"
    return render_template("editor_login.html", error=error)

@app.route("/edit/logout", methods=["GET", "POST"])
@login_required
def editor_logout():
    session.pop("editor")
    return redirect(request.args.get("next") or url_for("index"))

def word_form(word_index: int, raise_error: bool = True):
    errors = {}
    new = word_index not in d.DICT.index
    if raise_error and new:
        abort(404, "Запись в словаре с таким ID не найдена.")
    if request.method == 'POST':
        form_dict = {k: v for k, v in request.form.items() if v}
        d.DICT.loc[word_index, list(form_dict.keys())] = list(form_dict.values())
        d.update_dict()
        return redirect(url_for("edit_word", word_index=word_index))
    context = {
        "fieldsets": {
            "Слово": [("RSL", "РЖЯ"), ("Russian", "Русский"), ("Sources", "Источники")],
            "Пример": [("Example_RSL", "На РЖЯ"), ("Example_Russian", "На русском"), ("Example_sources", "Источники")],
            "Грамматика": [("Lemma", "Лемма"), ("GrammarMeaning", "Грамматические значения")]
        },
        "rsl_fields": ["RSL", "Lemma", "Example_RSL"]
    }
    if not new: context["current"] = dict(d.DICT.loc[word_index].dropna())
    return render_template(
        "word_form.html", word_index=word_index, errors=errors, **context
    )

@app.route("/edit/new", methods=["GET", "POST"])
@login_required
def create_word():
    return word_form(d.DICT.shape[0], raise_error=False)

@app.route("/edit/<int:word_index>", methods=["GET", "POST"])
@login_required
def edit_word(word_index: int):
    return word_form(word_index)

@app.post("/edit/delete/<int:word_index>")
@login_required
def delete_word(word_index: int):
    d.DICT.drop(index=word_index, inplace=True)
    d.DICT.reset_index(drop=True, inplace=True)
    d.update_dict()
    return redirect(url_for("edit"))