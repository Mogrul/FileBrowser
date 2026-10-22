from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")

from . import login, registration, files
bp.register_blueprint(login.bp)
bp.register_blueprint(registration.bp)
bp.register_blueprint(files.bp)