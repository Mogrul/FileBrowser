from datetime import datetime
from dataclasses import asdict

from flask import Blueprint, render_template, request, url_for

from filebrowser.app.decorators import authenticate, scope_needed
from filebrowser.app.util import send_error, get_entry_url
from filebrowser.database import database
from filebrowser.enums import ErrorMessage, EntryType
from filebrowser.models import User, Scope
from filebrowser.storage import storage
from filebrowser.util import format_bytes

bp = Blueprint("index", __name__)

@bp.route("/")
@scope_needed
@authenticate
def index(user: User, allowed_scopes: set[str], scope: Scope):
    data = request.args
    path_id = data.get("path")

    if path_id:
        entry = database.get_file_entry_by_id(path_id)

        if not entry:
            return send_error(ErrorMessage.PATH_NOT_FOUND)

        target_entry = scope.path / entry.path

    else:
        target_entry = scope.path

    file_entries = []
    for path in target_entry.iterdir():
        file_entry = database.get_file_entry_by_path(path)

        if not file_entry:
            file_entry = database.add_entry(scope.name, path)

        stat = file_entry.path.stat()
        size_str = format_bytes(stat.st_size)
        modified = datetime.fromtimestamp(stat.st_mtime)

        file_entries.append({
            "name": path.name,
            "type": file_entry.type,
            "id": file_entry.id,
            "url": get_entry_url(file_entry, scope.name),
            "size": size_str,
            "modified": modified.strftime("%d-%m-%Y"),
        })

    breadcrumbs = []
    for path in target_entry.parents:
        try:
            path.relative_to(scope.path)

        except ValueError:
            break


        file_entry = database.get_file_entry_by_path(path)
        if not file_entry:
            file_entry = database.add_entry(scope.name, path)

        if path == scope.path:
            url = url_for("index.index", scope=scope.name)

        else:
            url = get_entry_url(file_entry, scope.name)

        breadcrumbs.append({
            "name": path.name,
            "url": url
        })

    return render_template(
        "index.html",
        branding=asdict(storage.branding),
        allowed_scopes=allowed_scopes,
        current_scope=scope.name,
        entry_name=target_entry.name,
        file_entries=file_entries,
        breadcrumbs=list(reversed(breadcrumbs))
    )