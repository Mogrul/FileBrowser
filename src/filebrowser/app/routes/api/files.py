from flask import Blueprint, send_file, request, url_for

from filebrowser.app.decorators import authenticate
from filebrowser.app.util import send_error, send_success
from filebrowser.database import database
from filebrowser.enums import ErrorMessage
from filebrowser.globals import THUMBNAIL_DIR
from filebrowser.models import User
from filebrowser.util import thumbnail_image

bp = Blueprint("files", __name__, url_prefix="/files")

@bp.route("/image/<path:path>")
@authenticate
def image(user: User, allowed_scopes: set[str], path: str):
    file_entry = database.get_file_entry_by_id(path)

    if not file_entry:
        return send_error(ErrorMessage.PATH_NOT_FOUND)

    return send_file(file_entry.path, conditional=True)

@bp.route("/video/<path:path>")
@authenticate
def video(user: User, allowed_scopes: set[str], path: str):
    file_entry = database.get_file_entry_by_id(path)

    if not file_entry:
        return send_error(ErrorMessage.PATH_NOT_FOUND)

    return send_file(file_entry.path, conditional=True)

@bp.route("/<path:path>")
@authenticate
def other(user: User, allowed_scopes: set[str], path: str):
    file_entry = database.get_file_entry_by_id(path)

    if not file_entry:
        return send_error(ErrorMessage.PATH_NOT_FOUND)

    return send_file(file_entry.path, conditional=True)

@bp.route("/thumbnail/<path:path>")
@authenticate
def thumbnail(user: User, allowed_scopes: set[str], path: str):
    thumbnail_path = THUMBNAIL_DIR / f"{path}.webp"

    if not thumbnail_path.exists():
        return send_error(ErrorMessage.PATH_NOT_FOUND)

    return send_file(thumbnail_path, conditional=True)

@bp.post("/thumbnails")
@authenticate
def get_thumbnails(user: User, allowed_scopes: set[str]):
    data = request.get_json(silent=True) or {}
    ids = data.get("ids")

    if not isinstance(ids, list):
        return send_error(ErrorMessage.INVALID_REQUEST)

    thumbnails = []
    for entry_id in ids:
        entry = database.get_file_entry_by_id(entry_id)

        if not entry:
            continue

        thumbnail_path = THUMBNAIL_DIR / f"{entry.id}.webp"

        if not thumbnail_path.exists():
            result = thumbnail_image(entry.path, thumbnail_path)

            if not result:
                continue

        thumbnails.append({
            "id": entry.id,
            "url": url_for("api.files.thumbnail", path=entry_id)
        })

    return send_success(
        f"Found {len(thumbnails)} thumbnails for {len(ids)} entries.",
        code=200,
        data=thumbnails,
    )