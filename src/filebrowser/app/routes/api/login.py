import base64
import secrets
import time

from flask import Blueprint, request, session
from opaque_ke_py import opaque_ke_py

from filebrowser.app.decorators import no_login, authenticate
from filebrowser.enums import ErrorMessage, SuccessMessage
from filebrowser.app.util import send_error, send_success
from filebrowser.database import database
from filebrowser.globals import REQUEST_EXPIRATION
from filebrowser.models import PendingLogin, User
from filebrowser.storage import storage

bp = Blueprint("login", __name__, url_prefix="/login")

@bp.post("/logout")
@authenticate
def logout(user: User, allowed_scopes: set[str]):
    session.clear()

    return send_success(SuccessMessage.LOGOUT)

@bp.post("/start")
@no_login
def start():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    login_request = data.get("startLoginRequest")

    if (
        not isinstance(username, str)
        or not isinstance(login_request, str)
    ):
        return send_error(ErrorMessage.INVALID_REQUEST)

    login_request += "=" * (len(login_request) % 4)
    user = database.get_user(username)

    if not user:
        return send_error(ErrorMessage.USER_NOT_FOUND)

    result = opaque_ke_py.server_login_start(
        storage.opaque_setup,
        user.password_file,
        base64.urlsafe_b64decode(login_request),
        username.encode("utf-8"),
    )

    storage.cleanup_expired_requests()
    request_id = secrets.token_urlsafe(32)

    pending_login = PendingLogin(
        state=result.get_state(),
        username=username,
        expires=time.monotonic() + REQUEST_EXPIRATION
    )
    storage.add_pending_login(request_id, pending_login)

    return send_success(
        message=f"Started login request for {username}",
        code=200,
        loginResponse=base64.urlsafe_b64encode(result.get_message()).decode("ascii"),
        requestId=request_id,
    )

@bp.post("/finish")
@no_login
def finish():
    data = request.get_json(silent=True) or {}
    request_id = data.get("requestId")
    login_request = data.get("finishLoginRequest")

    if not isinstance(login_request, str):
        return send_error(ErrorMessage.INVALID_REQUEST)

    if not isinstance(login_request, str):
        return send_error(ErrorMessage.INVALID_REQUEST)

    pending_login = storage.get_pending_login(request_id)

    if not pending_login:
        return send_error(ErrorMessage.EXPIRED)

    login_request += "=" * (len(login_request) % 4)

    opaque_ke_py.server_login_finish(
        pending_login.state,
        base64.urlsafe_b64decode(login_request),
    )

    if not database.user_exists(pending_login.username):
        return send_error(ErrorMessage.USER_NOT_FOUND)

    user = database.get_user(pending_login.username)

    if not user:
        return send_error(ErrorMessage.USER_NOT_FOUND)

    database.update_user_last_logged_in(user.username)

    storage.remove_pending_login(request_id)
    session.clear()
    session.permanent = True

    session["data"] = {
        "username": user.username,
    }

    return send_success(SuccessMessage.LOGIN)
