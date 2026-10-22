import base64
import secrets
import time

from flask import Blueprint, request
from opaque_ke_py import opaque_ke_py

from filebrowser.app.decorators import no_login
from filebrowser.app.util import send_error, send_success
from filebrowser.database import database
from filebrowser.enums import ErrorMessage, SuccessMessage
from filebrowser.globals import REQUEST_EXPIRATION
from filebrowser.models import PendingRegistration, User
from filebrowser.storage import storage

bp = Blueprint("registration", __name__, url_prefix="/registration")

@bp.post("/start")
@no_login
def start():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    registration_request = data.get("registrationRequest")

    if (
        not isinstance(username, str)
        or not isinstance(registration_request, str)
    ):
        return send_error(ErrorMessage.INVALID_REQUEST)

    if database.user_exists(username):
        return send_error(ErrorMessage.USER_EXISTS)

    registration_request += "=" * (len(registration_request) % 4)
    result = opaque_ke_py.server_registration_start(
        storage.opaque_setup,
        base64.urlsafe_b64decode(registration_request),
        username.encode("utf-8"),
    )

    storage.cleanup_expired_requests()
    request_id = secrets.token_urlsafe(32)

    pending_registration = PendingRegistration(
        username=username,
        expires=time.monotonic() + REQUEST_EXPIRATION
    )
    storage.add_pending_registration(request_id, pending_registration)

    return send_success(
        message=f"Started registration request for {username}",
        code=200,
        registrationResponse=base64.urlsafe_b64encode(result.get_message()).decode("ascii"),
        requestId=request_id,
    )

@bp.post("/finish")
@no_login
def finish():
    data = request.get_json(silent=True) or {}
    request_id = data.get("requestId")
    registration_record = data.get("registrationRecord")

    if (
        not isinstance(registration_record, str)
        or not isinstance(request_id, str)
    ):
        return send_error(ErrorMessage.INVALID_REQUEST)

    storage.cleanup_expired_requests()
    pending_registration = storage.get_pending_registration(request_id)

    if not pending_registration:
        return send_error(ErrorMessage.EXPIRED)

    registration_record += "=" * (len(registration_record) % 4)
    result = opaque_ke_py.server_registration_finish(
        base64.urlsafe_b64decode(registration_record)
    )
    password_file = result.get_password_file()

    user = database.add_user(
        username=pending_registration.username,
        password_file=password_file,
    )

    if user is None:
        return send_error("Failed", 500)

    return send_success(SuccessMessage.REGISTRATION)