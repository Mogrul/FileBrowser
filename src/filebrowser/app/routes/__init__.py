from flask import Flask

from . import index, login, api

def register_all(app: Flask):
    app.register_blueprint(index.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(api.bp)
