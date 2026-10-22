from dataclasses import asdict

from flask import Blueprint, render_template

from filebrowser.app.decorators import no_login
from filebrowser.storage import storage

bp = Blueprint("login", __name__, url_prefix="/login")

@bp.route("/")
@no_login
def login():
    return render_template(
        "login.html",
        branding=asdict(storage.branding),
    )