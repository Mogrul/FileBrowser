import json
from datetime import timedelta
from pathlib import Path

SOURCE_DIR = Path.cwd() / "src"
STATIC_DIR = SOURCE_DIR / "static"
TEMPLATE_DIR = SOURCE_DIR / "templates"
JS_DIR = STATIC_DIR / "js"
KEYS_DIR = SOURCE_DIR / ".keys"

MANIFEST_PATH = JS_DIR / "manifest.json"
OPAQUE_SETUP_PATH = KEYS_DIR / "opaque_setup.enc"

MANIFEST_DATA = json.loads(open(MANIFEST_PATH).read())

SERVICE_NAME = "FILEBROWSER"
FLASK_KEY_NAME = "FLASK"
OPAQUE_KEY_NAME = "OPAQUE"

SESSION_LIFETIME = timedelta(days=7)