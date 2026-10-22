from flask import Blueprint, request

bp = Blueprint("login", __name__, url_prefix="/login")

@bp.post("/start")
def start():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    login_request = data.get("startLoginRequest")

    return {
        "username": username,
        "login_request": login_request
    }, 200

@bp.post("/finish")
def login():
    pass