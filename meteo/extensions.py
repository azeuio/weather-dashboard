from flask import request
from flask_babel import Babel


def get_locale():
    lang = request.accept_languages.best_match(["en", "fr"])
    print(f"Selected language: {lang}")
    return lang


babel = Babel()
