import logging
from functools import wraps

from flask import session, redirect, url_for, request

from filebrowser.app.util import send_error
from filebrowser.database import database
from filebrowser.enums import ErrorMessage
from filebrowser.storage import storage


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_data = session.get("data", {})

        if not session_data:
            return redirect(url_for("login.login"))

        username = session_data.get("username")

        if not username:
            session.clear()
            return redirect(url_for("login.login"))

        user = database.get_user(username)

        if not user:
            session.clear()
            return redirect(url_for("login.login"))

        allowed_scopes = set(user.scopes)
        allowed_scopes.update(storage.default_scopes)

        return func(*args, user=user, allowed_scopes=allowed_scopes, **kwargs)

    return wrapper

def no_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_data = session.get("data", {})

        if session_data:
            return redirect(url_for("index.index"))

        return func(*args, **kwargs)

    return wrapper

def scope_needed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        scope = request.args.get("scope")

        if not scope:
            if not storage.default_scopes:
                return send_error(ErrorMessage.NO_SCOPES)

            scope = next(iter(storage.default_scopes))

        scope = storage.scopes[scope]

        return func(*args, scope=scope, **kwargs)

    return wrapper