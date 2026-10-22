from flask import Flask

from . import index
from . import api

def register_all(app: Flask):
    app.register_blueprint(index.bp)
    app.register_blueprint(api.bp)