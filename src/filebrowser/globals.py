import json
from datetime import timedelta
from pathlib import Path

SOURCE_DIR = Path.cwd() / "src"
STATIC_DIR = SOURCE_DIR / "static"
TEMPLATE_DIR = SOURCE_DIR / "templates"
JS_DIR = STATIC_DIR / "js"
KEYS_DIR = SOURCE_DIR / ".keys"
THUMBNAIL_DIR = SOURCE_DIR / ".thumbnails"

MANIFEST_PATH = JS_DIR / "manifest.json"
OPAQUE_SETUP_PATH = KEYS_DIR / "opaque_setup.enc"
DATABASE_PATH = SOURCE_DIR / "filebrowser.db"
CONFIG_PATH = SOURCE_DIR / "config.toml"

MANIFEST_DATA = json.loads(open(MANIFEST_PATH).read())

SERVICE_NAME = "FILEBROWSER"
FLASK_KEY_NAME = "FLASK"
OPAQUE_KEY_NAME = "OPAQUE"

SESSION_LIFETIME = timedelta(days=7)
REQUEST_EXPIRATION = timedelta(minutes=10).total_seconds()

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov",
    ".m4v", ".avi", ".webm",
    ".flv", ".wmv", ".flv",
    ".ogg",
}

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg",
    ".webp", ".gif", ".jif",
    ".jfif", ".jfi", ".avif"
}

SOURCE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
JS_DIR.mkdir(parents=True, exist_ok=True)
KEYS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)