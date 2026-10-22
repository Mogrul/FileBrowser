from flask import url_for

from filebrowser.globals import MANIFEST_DATA

def get_ts_url(path: str) -> str:
    path = f"src/dev/ts/{path}"
    data = MANIFEST_DATA.get(path)

    if not data:
        raise RuntimeError(f"Path in vite manifest not found: {path}")

    return url_for("static", filename=f"js/{data['file']}")