from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")

from . import login
bp.register_blueprint(login.bp)